"""Message turn lifecycle repository.

Implements the ``plan.md`` section 5.3 workflow: claim one active turn
transactionally -> commit before providers -> scoped retrieval ->
generation -> guarded persistence.  All functions are pure database
work (no provider calls); the router commits between steps via
``request_transaction`` so no transaction spans a provider call.

Lifecycle invariants enforced here (``docs/v2-contracts.md`` section 5.3):

* **Idempotent send** via the partial unique
  ``(conversation_id, client_request_id)`` index: the same request key
  with different content raises :class:`DuplicateRequestConflict`; a
  duplicate of a *completed* turn returns the original persisted result
   (:attr:`Claim.replay_result`); a duplicate of the latest failed/expired
   turn is re-claimed so clients can retry by re-sending the same key.
* **One active turn** per conversation via the partial unique generation
  index: a second send while a turn is ``pending``/``generating``
  (unexpired) raises :class:`ActiveTurnInProgress`.  Expired claims are
  settled to ``failed`` (interrupted) before each claim, so a dead
  server process can never wedge a conversation.
* **Retry** serves only the latest user turn, and only when it is
  ``failed`` or an expired active turn (:func:`reclaim_turn_for_retry`).
* **Cancel** invalidates the generation token; a late provider response
  then fails the persist guard and cannot create an assistant row.
* **Source snapshot**: :func:`resolve_authorized_sources` captures the
  project's non-deleted ``Completed`` documents with their active index
  versions; the snapshot is stored in the user turn's ``metadata`` and
  re-validated before the assistant row is persisted.

Generation failures never delete the user row: it stays visible with its
ID/status for retry (``docs/v2-contracts.md`` section 2.3).
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.db.models import Conversation, Document, Message
from app.db.queries import get_owned_conversation, next_message_position
from app.repositories.conversations import NotFoundError, to_message_dto
from app.schemas.common import Citation
from app.schemas.messages import Message as MessageDto, TurnResponse
from app.schemas.services import AuthorizedSource, HistoryTurn

# A claimed turn must finish (including provider latency) within this
# lease; afterwards it is retriable as "interrupted" and a late response
# can no longer commit.
GENERATION_LEASE_SECONDS = 300
# Bounded prompt history (``project_db_auth_rag_flow_v2.md`` section 6.2):
# newest-first selection until both caps are reached.
HISTORY_MAX_MESSAGES = 20
HISTORY_CHAR_BUDGET = 12_000

ACTIVE_STATUSES = ("pending", "generating")
TERMINAL_STATUSES = ("completed", "failed", "cancelled")


class DuplicateRequestConflict(Exception):
    """Same idempotency key reused with different content (``409``)."""

    def __init__(self, *, message_id: UUID, conversation_id: UUID) -> None:
        super().__init__("This request key was already used with different content.")
        self.message_id = message_id
        self.conversation_id = conversation_id


class ActiveTurnInProgress(Exception):
    """Another turn is already generating in this conversation (``409``)."""

    def __init__(self, *, active_message_id: UUID, conversation_id: UUID) -> None:
        super().__init__("Another message is being answered in this conversation.")
        self.active_message_id = active_message_id
        self.conversation_id = conversation_id


class InvalidStateError(Exception):
    """Retry/cancel requested for an ineligible turn (``409``)."""


class NoReadySourcesError(Exception):
    """The project has no ready (Completed, non-deleted) sources (``409``)."""


class ClaimLostError(Exception):
    """A late generation can no longer commit (cancelled/expired/deleted)."""


class SnapshotMismatchError(ClaimLostError):
    """The authorized sources changed or became invalid mid-generation.

    Carries the terminal error ``code`` so the caller can mark the turn
    ``failed`` in a fresh transaction (the persist transaction itself
    rolls back and must not leave a half-written turn).
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class Claim:
    """A claimed (or replayed) user turn, ready for provider execution.

    For a fresh claim, :attr:`generation_token` and
    :attr:`generation_expires_at` fence the provider work and
    :attr:`snapshot` is the authorized-source snapshot recorded in the
    turn's metadata.  For a duplicate of an already-completed turn,
    :attr:`is_replay` is set and :attr:`replay_result` carries the
    original persisted turn (no provider call is needed).
    """

    user_message_id: UUID
    conversation_id: UUID
    content: str
    generation_token: UUID | None = None
    generation_expires_at: datetime | None = None
    snapshot: list[AuthorizedSource] = field(default_factory=list)
    client_request_id: UUID | None = None
    is_replay: bool = False
    replay_result: TurnResponse | None = None


# ---------------------------------------------------------------------------
# Claim step (transactional; caller commits before providers)
# ---------------------------------------------------------------------------


def claim_new_turn(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
    content: str,
    client_request_id: UUID,
) -> Claim:
    """Insert or reuse the user row for a new message submission.

    Must run inside a short transaction.  Raises :class:`NotFoundError`
    for missing/unowned scopes, :class:`DuplicateRequestConflict` for
    same-key/different-content, and :class:`ActiveTurnInProgress` when an
    unexpired turn is already generating.
    """
    conversation = _owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    _settle_expired_turns(session, conversation_id=conversation.id)

    existing = session.scalar(
        select(Message).where(
            Message.conversation_id == conversation.id,
            Message.role == "user",
            Message.client_request_id == client_request_id,
        )
    )
    if existing is not None:
        return _handle_duplicate(
            session,
            existing=existing,
            content=content,
            conversation_id=conversation.id,
        )

    active = _active_turn(session, conversation_id=conversation.id)
    if active is not None:
        raise ActiveTurnInProgress(
            active_message_id=active.id, conversation_id=conversation.id
        )

    claim = _insert_user_turn(
        session,
        conversation_id=conversation.id,
        content=content,
        client_request_id=client_request_id,
    )
    return claim


def reclaim_turn_for_retry(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
    message_id: UUID,
    client_request_id: UUID | None,
) -> Claim:
    """Re-claim the latest eligible failed/interrupted user turn.

    Retrying never appends a second user message or a second assistant
    reply (the partial unique ``reply_to_message_id`` index enforces
    exactly one reply).  Only the most recent user turn is eligible, and
    only when it is ``failed`` or an expired active turn; an older turn
    is rejected so its answer cannot be inserted into later history.

    A ``client_request_id`` sent with the retry must match the original
    turn's key (idempotent retry); a mismatch raises
    :class:`DuplicateRequestConflict`.
    """
    conversation = _owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    _settle_expired_turns(session, conversation_id=conversation.id)

    message = session.scalar(
        select(Message).where(
            Message.id == message_id,
            Message.conversation_id == conversation.id,
            Message.role == "user",
        )
    )
    if message is None:
        raise NotFoundError(f"message not found: {message_id}")
    if client_request_id is not None and client_request_id != message.client_request_id:
        raise DuplicateRequestConflict(
            message_id=message.id, conversation_id=conversation.id
        )
    return _retry_failed_turn(session, message=message, conversation_id=conversation.id)


def _retry_failed_turn(
    session: Session, *, message: Message, conversation_id: UUID
) -> Claim:
    """Apply identical eligibility to explicit retry and same-key resend."""
    latest = session.scalar(
        select(Message.position)
        .where(
            Message.conversation_id == conversation_id,
            Message.role == "user",
        )
        .order_by(Message.position.desc())
        .limit(1)
    )
    if latest is None or message.position != latest:
        raise InvalidStateError("Only the latest turn can be retried.")
    if message.generation_status in ACTIVE_STATUSES:
        raise ActiveTurnInProgress(
            active_message_id=message.id, conversation_id=conversation_id
        )
    if message.generation_status != "failed":
        raise InvalidStateError(
            "Only a failed or interrupted turn can be retried.",
        )
    active = _active_turn(session, conversation_id=conversation_id)
    if active is not None:
        raise ActiveTurnInProgress(
            active_message_id=active.id, conversation_id=conversation_id
        )
    return _reactivate(
        session,
        message=message,
        conversation_id=conversation_id,
    )


def _handle_duplicate(
    session: Session,
    *,
    existing: Message,
    content: str,
    conversation_id: UUID,
) -> Claim:
    if existing.content != content:
        raise DuplicateRequestConflict(
            message_id=existing.id, conversation_id=conversation_id
        )
    status = existing.generation_status
    if status == "completed":
        return Claim(
            user_message_id=existing.id,
            conversation_id=conversation_id,
            content=existing.content,
            client_request_id=existing.client_request_id,
            is_replay=True,
            replay_result=_load_completed_turn(
                session,
                user_message=existing,
                conversation_id=conversation_id,
            ),
        )
    if status in ACTIVE_STATUSES:
        raise ActiveTurnInProgress(
            active_message_id=existing.id, conversation_id=conversation_id
        )
    if status == "failed":
        # Same-key resend of a failed turn re-claims it (same as retry).
        return _retry_failed_turn(session, message=existing, conversation_id=conversation_id)
    raise InvalidStateError("This turn was cancelled; submit a new request.")


def _insert_user_turn(
    session: Session,
    *,
    conversation_id: UUID,
    content: str,
    client_request_id: UUID,
) -> Claim:
    now = utcnow()
    token = uuid.uuid4()
    expires_at = now + timedelta(seconds=GENERATION_LEASE_SECONDS)
    position = next_message_position(session, conversation_id=conversation_id)
    row = Message(
        conversation_id=conversation_id,
        role="user",
        content=content,
        position=position,
        client_request_id=client_request_id,
        generation_status="generating",
        generation_token=token,
        generation_expires_at=expires_at,
    )
    session.add(row)
    session.flush()
    return Claim(
        user_message_id=row.id,
        conversation_id=conversation_id,
        content=content,
        generation_token=token,
        generation_expires_at=expires_at,
        client_request_id=client_request_id,
    )


def _reactivate(
    session: Session,
    *,
    message: Message,
    conversation_id: UUID,
) -> Claim:
    now = utcnow()
    token = uuid.uuid4()
    expires_at = now + timedelta(seconds=GENERATION_LEASE_SECONDS)
    message.generation_status = "generating"
    message.generation_token = token
    message.generation_expires_at = expires_at
    session.flush()
    return Claim(
        user_message_id=message.id,
        conversation_id=conversation_id,
        content=message.content,
        generation_token=token,
        generation_expires_at=expires_at,
        client_request_id=message.client_request_id,
    )


def _settle_expired_turns(session: Session, *, conversation_id: UUID) -> None:
    """Force expired active turns to ``failed`` (interrupted).

    Generation expiry is a *logical* fence (the token check at persist
    time); this sweep just keeps the rows honest so they become
    retriable and the one-active-turn partial index never wedges on a
    crashed server process.
    """
    now = utcnow()
    session.execute(
        update(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.role == "user",
            Message.generation_status.in_(ACTIVE_STATUSES),
            Message.generation_expires_at <= now,
        )
        .values(
            generation_status="failed",
            generation_token=None,
            generation_expires_at=None,
        )
    )
    session.flush()


def _active_turn(session: Session, *, conversation_id: UUID) -> Message | None:
    """Return the unexpired pending/generating user turn, if any."""
    now = utcnow()
    return session.scalar(
        select(Message).where(
            Message.conversation_id == conversation_id,
            Message.role == "user",
            Message.generation_status.in_(ACTIVE_STATUSES),
            Message.generation_expires_at > now,
        )
    )


# ---------------------------------------------------------------------------
# Context + snapshot (transactional reads)
# ---------------------------------------------------------------------------


def select_history_rows(
    rows_desc: Sequence[Message],
    *,
    max_messages: int = HISTORY_MAX_MESSAGES,
    char_budget: int = HISTORY_CHAR_BUDGET,
) -> list[Message]:
    """Select the newest rows within the prompt budget (pure helper).

    Rows are given newest-first (descending ``position``); the result is
    chronological (ascending).  The newest row is always included, even
    if it alone exceeds the character budget, so context is never empty
    when completed history exists.
    """
    selected: list[Message] = []
    used = 0
    for row in rows_desc:
        if len(selected) >= max_messages:
            break
        if selected and used + len(row.content) > char_budget:
            break
        selected.append(row)
        used += len(row.content)
    selected.reverse()
    return selected


def load_history_turns(
    session: Session,
    *,
    conversation_id: UUID,
    max_messages: int = HISTORY_MAX_MESSAGES,
    char_budget: int = HISTORY_CHAR_BUDGET,
) -> list[HistoryTurn]:
    """Load recent completed turns as generation context.

    Only completed user turns and their assistant replies qualify;
    failed/cancelled/pending/generating turns are excluded.  The current
    (claimed, still ``generating``) question is not part of the result —
    the caller adds it exactly once to the assembled prompt.
    """
    rows = list(
        session.scalars(
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                (Message.role == "assistant")
                | (
                    (Message.role == "user")
                    & (Message.generation_status == "completed")
                ),
            )
            .order_by(Message.position.desc())
        )
    )
    history_rows = select_history_rows(
        rows, max_messages=max_messages, char_budget=char_budget
    )
    return [
        HistoryTurn(role=row.role, content=row.content, position=row.position)
        for row in history_rows
    ]


def resolve_authorized_sources(
    session: Session, *, user_id: UUID, project_id: UUID
) -> list[AuthorizedSource]:
    """Resolve the project's retrievable (document, active version) pairs.

    Only non-deleted ``Completed`` documents with a published
    ``active_index_version`` qualify.  Each result is an exact pair —
    retrieval must never mix a document from one version with the
    version of another document.  Empty results raise
    :class:`NoReadySourcesError` (never an unscoped search).
    """
    from app.db.queries import get_owned_project

    if get_owned_project(session, user_id=user_id, project_id=project_id) is None:
        raise NotFoundError(f"project not found: {project_id}")
    rows = list(
        session.scalars(
            select(Document).where(
                Document.project_id == project_id,
                Document.status == "Completed",
                Document.deleted_at.is_(None),
                Document.active_index_version.is_not(None),
            )
        )
    )
    sources = [
        AuthorizedSource(
            document_id=row.id,
            index_version=row.active_index_version,
            file_name=row.file_name,
        )
        for row in rows
        if row.active_index_version is not None
    ]
    sources.sort(key=lambda s: (str(s.document_id), str(s.index_version)))
    if not sources:
        raise NoReadySourcesError(
            "No completed documents are available to answer this question."
        )
    return sources


def snapshot_document_ids(sources: Sequence[AuthorizedSource]) -> list[dict[str, str]]:
    """Serialize an authorized-source snapshot for turn metadata."""
    return [
        {
            "documentId": str(source.document_id),
            "indexVersion": str(source.index_version),
            "fileName": source.file_name,
        }
        for source in sources
    ]


def record_snapshot(
    session: Session,
    *,
    user_message_id: UUID,
    snapshot: Sequence[AuthorizedSource],
) -> None:
    """Persist the source snapshot into the claimed turn's metadata."""
    row = session.get(Message, user_message_id)
    if row is None:
        return
    metadata = dict(row.message_metadata or {})
    metadata["sourceSnapshot"] = snapshot_document_ids(snapshot)
    row.message_metadata = metadata
    session.flush()


def snapshot_matches(snapshot: Sequence[AuthorizedSource], current: Sequence[AuthorizedSource]) -> bool:
    """True when the authorized pairs are identical (order-insensitive)."""
    return {(s.document_id, s.index_version) for s in snapshot} == {
        (s.document_id, s.index_version) for s in current
    }


# ---------------------------------------------------------------------------
# Terminal steps (transactional)
# ---------------------------------------------------------------------------


def persist_assistant_answer(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
    user_message_id: UUID,
    generation_token: UUID,
    snapshot: Sequence[AuthorizedSource],
    answer: str,
    citations: Sequence[Citation],
    model: str,
    latency_ms: int,
) -> TurnResponse:
    """Persist the assistant row and finalize the user turn.

    Commits only when the generation claim is still current and
    unexpired, the source snapshot is still valid, and the
    project/conversation is still accessible.  Raises
    :class:`ClaimLostError` otherwise (the late answer is discarded and
    no assistant row is created).  A snapshot mismatch raises
    :class:`SnapshotMismatchError` so the caller marks the turn
    ``failed`` in a fresh transaction, letting the client retry with
    fresh sources.
    """
    conversation = get_owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    if conversation is None:
        raise ClaimLostError("conversation no longer accessible")
    user_message = session.scalar(
        select(Message).where(
            Message.id == user_message_id,
            Message.conversation_id == conversation_id,
            Message.role == "user",
        )
    )
    if user_message is None:
        raise ClaimLostError("user turn no longer exists")
    now = utcnow()
    if (
        user_message.generation_status not in ACTIVE_STATUSES
        or user_message.generation_token != generation_token
        or (
            user_message.generation_expires_at is not None
            and user_message.generation_expires_at <= now
        )
    ):
        raise ClaimLostError("generation claim is stale (cancelled or expired)")
    try:
        current = resolve_authorized_sources(
            session, user_id=user_id, project_id=project_id
        )
    except (NoReadySourcesError, NotFoundError) as exc:
        raise SnapshotMismatchError(
            "snapshot_invalid", "source snapshot no longer valid"
        ) from exc
    if not snapshot_matches(snapshot, current):
        raise SnapshotMismatchError(
            "snapshot_changed", "source snapshot changed during generation"
        )

    position = next_message_position(session, conversation_id=conversation_id)
    assistant = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=answer,
        position=position,
        citations=[
            citation.model_dump(mode="json", by_alias=True) for citation in citations
        ],
        message_metadata={
            "model": model,
            "latencyMs": latency_ms,
            "sourceSnapshot": snapshot_document_ids(snapshot),
        },
        reply_to_message_id=user_message.id,
    )
    user_message.generation_status = "completed"
    user_message.generation_token = None
    user_message.generation_expires_at = None
    session.add(assistant)
    session.flush()
    return TurnResponse(
        user_message=to_message_dto(user_message),
        assistant_message=to_message_dto(assistant),
    )


def mark_turn_failed(
    session: Session,
    *,
    user_message_id: UUID,
    generation_token: UUID,
    error_code: str,
    error_message: str,
) -> bool:
    """Mark an active turn ``failed`` when the claim is still current.

    Returns True when the row was updated, False when the claim is stale
    (e.g. the user already cancelled) — a cancelled turn is never
    resurrected to ``failed``.
    """
    row = session.scalar(
        select(Message).where(
            Message.id == user_message_id,
            Message.role == "user",
        )
    )
    if row is None:
        return False
    if (
        row.generation_status not in ACTIVE_STATUSES
        or row.generation_token != generation_token
    ):
        return False
    metadata = dict(row.message_metadata or {})
    metadata["error"] = {
        "code": error_code,
        "message": error_message[:500],
        "at": utcnow().isoformat(),
    }
    row.message_metadata = metadata
    row.generation_status = "failed"
    row.generation_token = None
    row.generation_expires_at = None
    session.flush()
    return True


def cancel_turn(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
    message_id: UUID,
) -> tuple[MessageDto, bool]:
    """Cancel the active turn; the token is invalidated so late answers die.

    The persisted user message stays visible with
    ``generationStatus: "cancelled"``.  Cancelling an already-cancelled
    turn is idempotent (returns the same message).  Completed/failed
    turns raise :class:`InvalidStateError`.
    """
    conversation = _owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    row = session.scalar(
        select(Message).where(
            Message.id == message_id,
            Message.conversation_id == conversation.id,
            Message.role == "user",
        )
    )
    if row is None:
        raise NotFoundError(f"message not found: {message_id}")
    if row.generation_status in ACTIVE_STATUSES:
        row.generation_status = "cancelled"
        row.generation_token = None
        row.generation_expires_at = None
        session.flush()
        return to_message_dto(row), True
    if row.generation_status == "cancelled":
        return to_message_dto(row), True
    raise InvalidStateError("Only an active turn can be cancelled.")


def get_turn_status(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
    message_id: UUID,
) -> MessageDto:
    """Return the current user-turn DTO for reconciliation after disconnect."""
    _owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    row = session.scalar(
        select(Message).where(
            Message.id == message_id,
            Message.conversation_id == conversation_id,
            Message.role == "user",
        )
    )
    if row is None:
        raise NotFoundError(f"message not found: {message_id}")
    return to_message_dto(row)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _owned_conversation(session, *, user_id, project_id, conversation_id) -> Conversation:
    conversation = get_owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    if conversation is None:
        raise NotFoundError(f"conversation not found: {conversation_id}")
    return conversation


def _load_completed_turn(session, *, user_message, conversation_id) -> TurnResponse:
    assistant = session.scalar(
        select(Message).where(
            Message.conversation_id == conversation_id,
            Message.role == "assistant",
            Message.reply_to_message_id == user_message.id,
        )
    )
    if assistant is None:
        # A completed user turn without its reply is an integrity
        # violation; treat it as an error the client cannot resolve.
        raise ClaimLostError("completed turn has no assistant reply")
    return TurnResponse(
        user_message=to_message_dto(user_message),
        assistant_message=to_message_dto(assistant),
    )


def _fail_turn_locked(user_message: Message, *, code: str) -> None:
    user_message.generation_status = "failed"
    user_message.generation_token = None
    user_message.generation_expires_at = None
    metadata = dict(user_message.message_metadata or {})
    metadata["error"] = {"code": code, "message": "Sources changed while answering."}
    user_message.message_metadata = metadata


__all__ = [
    "ACTIVE_STATUSES",
    "ActiveTurnInProgress",
    "Claim",
    "ClaimLostError",
    "DuplicateRequestConflict",
    "GENERATION_LEASE_SECONDS",
    "HISTORY_CHAR_BUDGET",
    "HISTORY_MAX_MESSAGES",
    "InvalidStateError",
    "NoReadySourcesError",
    "SnapshotMismatchError",
    "TERMINAL_STATUSES",
    "cancel_turn",
    "claim_new_turn",
    "get_turn_status",
    "load_history_turns",
    "mark_turn_failed",
    "persist_assistant_answer",
    "record_snapshot",
    "reclaim_turn_for_retry",
    "resolve_authorized_sources",
    "select_history_rows",
    "snapshot_document_ids",
    "snapshot_matches",
]

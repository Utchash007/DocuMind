"""Message routes and persisted-turn orchestration.

Turn lifecycle (``docs/v2-contracts.md`` section 5.3): claim
transactionally -> commit -> scoped retrieval + generation -> guarded
persistence.  No database transaction spans a provider call; success
returns ``{userMessage, assistantMessage}`` only after persistence.
Generation failures retain the user message with its ID/status for
retry, and a browser disconnect is reconciled by re-fetching persisted
messages (or the turn status).

Transaction map for POST/retry:

* tx1 â€” claim (insert/reuse user row); a duplicate of a completed turn
  returns the original persisted result immediately (no provider call).
* tx2 â€” resolve authorized sources + record the snapshot on the turn.
  An empty ready set fails the turn (user row retained) with
  ``409 no_ready_sources`` â€” never an unscoped search.
* providers â€” bounded history load, scoped retrieval, Groq generation.
* tx3 â€” persist assistant + citations guarded by the generation
  token, snapshot validity, and scope liveness; a cancelled/expired/
  deleted turn cannot commit.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from app.api.conversations import (
    PrincipalDep,
    SessionFactoryDep,
    api_error,
)
from app.rag.generation import MODEL_NAME, GenerationError
from app.rag.retrieval import IndexUnavailableError
from app.rag.retrieval import NoReadySourcesError as RetrievalNoReadySources
from app.repositories import conversations as conversations_repo
from app.repositories import messages as lifecycle
from app.repositories.conversations import CursorError, NotFoundError
from app.repositories.messages import (
    ActiveTurnInProgress,
    ClaimLostError,
    DuplicateRequestConflict,
    InvalidStateError,
    NoReadySourcesError,
    SnapshotMismatchError,
)
from app.schemas.common import ErrorCode, PaginatedResponse
from app.schemas.messages import (
    Message as MessageDto,
    MessageCancelResponse,
    MessageCreateRequest,
    MessageRetryRequest,
    TurnResponse,
)
from app.schemas.services import GeneratedAnswer

router = APIRouter(prefix="/projects/{project_id}/conversations/{conversation_id}/messages", tags=["messages"])


def get_answer_generator_dep() -> Callable[..., GeneratedAnswer]:
    """Return the production answer generator (Groq/Instructor).

    Tests override this dependency with a deterministic fake.  Handlers
    pass ``user_id``/``project_id`` alongside the frozen
    ``(question, history, authorized_sources)`` triple so retrieval is
    always scoped; the generator itself performs no row writes.
    """
    from app.rag import generation as generation_mod

    def _generate(
        *,
        question: str,
        history,
        authorized_sources,
        user_id=None,
        project_id=None,
        **_kwargs,
    ) -> GeneratedAnswer:
        return generation_mod.generate_answer(
            question=question,
            history=history,
            authorized_sources=authorized_sources,
            user_id=user_id,
            project_id=project_id,
        )

    return _generate


AnswerGeneratorDep = Annotated[Callable[..., GeneratedAnswer], Depends(get_answer_generator_dep)]


@router.get("", response_model=PaginatedResponse[MessageDto], response_model_by_alias=True)
def list_messages(
    project_id: Annotated[UUID, Path()],
    conversation_id: Annotated[UUID, Path()],
    principal: PrincipalDep,
    factory: SessionFactoryDep,
    cursor: Annotated[str | None, Query(description="Opaque nextCursor from the previous page")] = None,
    limit: Annotated[int, Query(ge=1, le=200, description="Bounded page size (1-200)")] = 50,
) -> PaginatedResponse[MessageDto]:
    """Paginated history in chronological (``position``) order."""
    from app.db.session import request_transaction

    try:
        with request_transaction(factory) as session:
            return conversations_repo.list_messages(
                session,
                user_id=principal.id,
                project_id=project_id,
                conversation_id=conversation_id,
                cursor=cursor,
                limit=limit,
            )
    except NotFoundError as exc:
        raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
    except CursorError as exc:
        raise api_error(422, ErrorCode.VALIDATION_ERROR, str(exc)) from exc


@router.post("", response_model=TurnResponse, response_model_by_alias=True)
def post_message(
    project_id: Annotated[UUID, Path()],
    conversation_id: Annotated[UUID, Path()],
    body: MessageCreateRequest,
    principal: PrincipalDep,
    factory: SessionFactoryDep,
    answer_generator: AnswerGeneratorDep,
) -> TurnResponse:
    """Submit ``{content, clientRequestId}`` and return the persisted turn.

    The user message is persisted before any provider call; the
    assistant row is persisted (and returned) only when the generation
    claim is still current and the source snapshot is still valid.
    A duplicate of a completed request returns the original result.
    """
    claim = _claim_tx(
        factory=factory,
        project_id=project_id,
        conversation_id=conversation_id,
        user_id=principal.id,
        content=body.content,
        client_request_id=body.client_request_id,
    )
    if claim.is_replay:
        assert claim.replay_result is not None
        return claim.replay_result
    return _run_claimed_turn(
        user_id=principal.id,
        project_id=project_id,
        conversation_id=conversation_id,
        claim=claim,
        factory=factory,
        answer_generator=answer_generator,
    )


@router.post("/{message_id}/retry", response_model=TurnResponse, response_model_by_alias=True)
def retry_message(
    project_id: Annotated[UUID, Path()],
    conversation_id: Annotated[UUID, Path()],
    message_id: Annotated[UUID, Path()],
    body: MessageRetryRequest,
    principal: PrincipalDep,
    factory: SessionFactoryDep,
    answer_generator: AnswerGeneratorDep,
) -> TurnResponse:
    """Retry the latest failed/interrupted user turn (no new user row)."""
    from app.db.session import request_transaction

    try:
        with request_transaction(factory) as session:
            claim = lifecycle.reclaim_turn_for_retry(
                session,
                user_id=principal.id,
                project_id=project_id,
                conversation_id=conversation_id,
                message_id=message_id,
                client_request_id=body.client_request_id,
            )
    except NotFoundError as exc:
        raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
    except DuplicateRequestConflict as exc:
        raise api_error(
            409,
            ErrorCode.DUPLICATE_REQUEST_CONFLICT,
            str(exc),
            message_id=exc.message_id,
            conversation_id=exc.conversation_id,
            project_id=project_id,
        ) from exc
    except ActiveTurnInProgress as exc:
        raise api_error(
            409,
            ErrorCode.ACTIVE_TURN_IN_PROGRESS,
            str(exc),
            message_id=exc.active_message_id,
            conversation_id=exc.conversation_id,
            project_id=project_id,
        ) from exc
    except InvalidStateError as exc:
        raise api_error(
            409,
            ErrorCode.INVALID_STATE,
            str(exc),
            message_id=message_id,
            conversation_id=conversation_id,
            project_id=project_id,
        ) from exc
    return _run_claimed_turn(
        user_id=principal.id,
        project_id=project_id,
        conversation_id=conversation_id,
        claim=claim,
        factory=factory,
        answer_generator=answer_generator,
    )


@router.post("/{message_id}/cancel", response_model=MessageCancelResponse, response_model_by_alias=True)
def cancel_message(
    project_id: Annotated[UUID, Path()],
    conversation_id: Annotated[UUID, Path()],
    message_id: Annotated[UUID, Path()],
    principal: PrincipalDep,
    factory: SessionFactoryDep,
) -> MessageCancelResponse:
    """Cancel the active turn; a late provider response cannot commit."""
    from app.db.session import request_transaction

    try:
        with request_transaction(factory) as session:
            message, cancelled = lifecycle.cancel_turn(
                session,
                user_id=principal.id,
                project_id=project_id,
                conversation_id=conversation_id,
                message_id=message_id,
            )
    except NotFoundError as exc:
        raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
    except InvalidStateError as exc:
        raise api_error(
            409,
            ErrorCode.INVALID_STATE,
            str(exc),
            message_id=message_id,
            conversation_id=conversation_id,
            project_id=project_id,
        ) from exc
    return MessageCancelResponse(user_message=message, cancelled=cancelled)


# ---------------------------------------------------------------------------
# Turn orchestration
# ---------------------------------------------------------------------------


def _claim_tx(
    *,
    factory,
    project_id: UUID,
    conversation_id: UUID,
    user_id: UUID,
    content: str,
    client_request_id: UUID,
):
    """tx1: claim (insert/reuse the user row)."""
    from app.db.session import request_transaction

    try:
        with request_transaction(factory) as session:
            return lifecycle.claim_new_turn(
                session,
                user_id=user_id,
                project_id=project_id,
                conversation_id=conversation_id,
                content=content,
                client_request_id=client_request_id,
            )
    except NotFoundError as exc:
        raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
    except DuplicateRequestConflict as exc:
        raise api_error(
            409,
            ErrorCode.DUPLICATE_REQUEST_CONFLICT,
            str(exc),
            message_id=exc.message_id,
            conversation_id=exc.conversation_id,
            project_id=project_id,
        ) from exc
    except ActiveTurnInProgress as exc:
        raise api_error(
            409,
            ErrorCode.ACTIVE_TURN_IN_PROGRESS,
            str(exc),
            message_id=exc.active_message_id,
            conversation_id=exc.conversation_id,
            project_id=project_id,
        ) from exc
    except InvalidStateError as exc:
        raise api_error(
            409,
            ErrorCode.INVALID_STATE,
            str(exc),
            conversation_id=conversation_id,
            project_id=project_id,
        ) from exc
    except ClaimLostError as exc:
        # A completed duplicate whose assistant row is missing is an
        # integrity violation (unreachable while persist creates both
        # rows atomically); surface it as an unexpected failure.
        raise api_error(
            500,
            ErrorCode.INTERNAL_ERROR,
            "This turn could not be reconciled; please retry.",
            conversation_id=conversation_id,
            project_id=project_id,
        ) from exc


def _run_claimed_turn(
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
    claim,
    factory,
    answer_generator: Callable[..., GeneratedAnswer],
) -> TurnResponse:
    """tx2 (snapshot) -> providers -> tx3 (guarded persist)."""
    from app.db.session import request_transaction

    assert claim.generation_token is not None
    # tx2: resolve authorized sources and record the snapshot. The user
    # row (inserted in tx1) survives an empty ready set: the turn is
    # failed and the error is useful â€” never an unscoped search.
    try:
        with request_transaction(factory) as session:
            snapshot = lifecycle.resolve_authorized_sources(
                session, user_id=user_id, project_id=project_id
            )
            claim.snapshot = snapshot
            lifecycle.record_snapshot(
                session,
                user_message_id=claim.user_message_id,
                snapshot=snapshot,
            )
    except NoReadySourcesError as exc:
        _mark_failed(
            factory=factory,
            user_message_id=claim.user_message_id,
            generation_token=claim.generation_token,
            error_code=ErrorCode.NO_READY_SOURCES.value,
            error_message=str(exc),
        )
        raise api_error(
            409,
            ErrorCode.NO_READY_SOURCES,
            str(exc),
            message_id=claim.user_message_id,
            conversation_id=conversation_id,
            project_id=project_id,
        ) from exc
    except NotFoundError as exc:
        raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc

    # Bounded recent completed history (current question added once by
    # the prompt builder; failed/cancelled turns excluded).
    try:
        with request_transaction(factory) as session:
            history = lifecycle.load_history_turns(
                session, conversation_id=conversation_id
            )
    except Exception as exc:  # unexpected DB failure: fail the turn, stay retryable
        _mark_failed(
            factory=factory,
            user_message_id=claim.user_message_id,
            generation_token=claim.generation_token,
            error_code=ErrorCode.INTERNAL_ERROR.value,
            error_message=f"History load failed: {exc}",
        )
        raise api_error(
            500,
            ErrorCode.INTERNAL_ERROR,
            "Failed to prepare the answer.",
            message_id=claim.user_message_id,
            conversation_id=conversation_id,
            project_id=project_id,
        ) from exc

    started = time.perf_counter()
    try:
        generated = answer_generator(
            question=claim.content,
            history=history,
            authorized_sources=claim.snapshot,
            user_id=user_id,
            project_id=project_id,
        )
    except (NoReadySourcesError, RetrievalNoReadySources) as exc:
        _mark_failed(
            factory=factory,
            user_message_id=claim.user_message_id,
            generation_token=claim.generation_token,
            error_code=ErrorCode.NO_READY_SOURCES.value,
            error_message=str(exc),
        )
        raise api_error(
            409,
            ErrorCode.NO_READY_SOURCES,
            str(exc),
            message_id=claim.user_message_id,
            conversation_id=conversation_id,
            project_id=project_id,
        ) from exc
    except (IndexUnavailableError, GenerationError) as exc:
        _mark_failed(
            factory=factory,
            user_message_id=claim.user_message_id,
            generation_token=claim.generation_token,
            error_code=ErrorCode.SERVICE_UNAVAILABLE.value,
            error_message=str(exc),
        )
        raise api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Answer generation is temporarily unavailable. Please retry.",
            message_id=claim.user_message_id,
            conversation_id=conversation_id,
            project_id=project_id,
        ) from exc
    except Exception as exc:  # defensive: never leak a provider payload
        _mark_failed(
            factory=factory,
            user_message_id=claim.user_message_id,
            generation_token=claim.generation_token,
            error_code=ErrorCode.INTERNAL_ERROR.value,
            error_message=f"Answer generation failed: {exc}",
        )
        raise api_error(
            500,
            ErrorCode.INTERNAL_ERROR,
            "Answer generation failed.",
            message_id=claim.user_message_id,
            conversation_id=conversation_id,
            project_id=project_id,
        ) from exc
    latency_ms = int((time.perf_counter() - started) * 1000)

    # tx3: persist guarded by token, snapshot, and scope liveness.
    try:
        with request_transaction(factory) as session:
            return lifecycle.persist_assistant_answer(
                session,
                user_id=user_id,
                project_id=project_id,
                conversation_id=conversation_id,
                user_message_id=claim.user_message_id,
                generation_token=claim.generation_token,
                snapshot=claim.snapshot,
                answer=generated.answer,
                citations=generated.citations,
                model=MODEL_NAME,
                latency_ms=latency_ms,
            )
    except ClaimLostError as exc:
        if isinstance(exc, SnapshotMismatchError):
            # The persist transaction rolled back; mark the turn failed
            # in its own token-guarded transaction so the client can
            # retry with fresh sources (the answer is discarded).
            _mark_failed(
                factory=factory,
                user_message_id=claim.user_message_id,
                generation_token=claim.generation_token,
                error_code=exc.code,
                error_message=str(exc),
            )
        try:
            with request_transaction(factory) as session:
                status = lifecycle.get_turn_status(
                    session,
                    user_id=user_id,
                    project_id=project_id,
                    conversation_id=conversation_id,
                    message_id=claim.user_message_id,
                ).generation_status
        except NotFoundError:
            status = None
        if status is None:
            raise api_error(
                404,
                ErrorCode.NOT_FOUND,
                "The conversation is no longer available.",
                conversation_id=conversation_id,
                project_id=project_id,
            ) from exc
        message = (
            "This turn was cancelled and its answer was discarded."
            if status == "cancelled"
            else "This turn can no longer be answered; please retry."
        )
        raise api_error(
            409,
            ErrorCode.INVALID_STATE,
            message,
            message_id=claim.user_message_id,
            conversation_id=conversation_id,
            project_id=project_id,
        ) from exc


def _mark_failed(*, factory, user_message_id: UUID, generation_token: UUID, error_code: str, error_message: str) -> bool:
    """Best-effort failure mark (own transaction, token-guarded)."""
    from app.db.session import request_transaction

    try:
        with request_transaction(factory) as session:
            return lifecycle.mark_turn_failed(
                session,
                user_message_id=user_message_id,
                generation_token=generation_token,
                error_code=error_code,
                error_message=error_message,
            )
    except Exception:  # never mask the real error with a cleanup failure
        return False


__all__ = ["get_answer_generator_dep", "router"]

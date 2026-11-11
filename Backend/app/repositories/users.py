"""Application-user repository: bootstrap, lookup, and profile updates.

Bootstrap rule: upsert by the *verified*
``appwrite_user_id`` only.  The unique constraint on that column makes
concurrent first requests resolve to a single row; a savepoint-guarded
insert absorbs the loser's unique violation and re-reads the winner.
Emails are normalized (trim/lowercase) and synchronized on every
bootstrap, but a verified-email change whose new address belongs to a
*different* identity is never merged: an existing row keeps its email,
and a first-login collision raises a ``conflict`` instead of merging
two identities.

All functions run inside the caller's short transaction
(``request_transaction``); they never call Appwrite or any provider.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.errors import conflict
from app.db.models import User
from app.schemas.users import derive_onboarding_completed


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user(session: Session, user_id: UUID) -> User | None:
    return session.get(User, user_id)


def _find_by_appwrite_id(session: Session, appwrite_user_id: str) -> User | None:
    return session.scalar(
        select(User).where(User.appwrite_user_id == appwrite_user_id)
    )


def _find_by_email(session: Session, email: str) -> User | None:
    return session.scalar(select(User).where(User.email == email))


def _sync_email(session: Session, user: User, email: str) -> None:
    """Adopt the verified email unless another identity already owns it."""
    if user.email == email:
        return
    owner = _find_by_email(session, email)
    if owner is not None and owner.id != user.id:
        # Never merge identities: keep the existing email.
        return
    user.email = email


def bootstrap_user(
    session: Session,
    *,
    appwrite_user_id: str,
    email: str,
) -> User:
    """Return the row for ``appwrite_user_id``, creating it on first login.

    Creation stores only the verified identity and email; profile fields
    stay NULL and ``onboarding_completed`` starts ``False``.
    """
    normalized = normalize_email(email)
    existing = _find_by_appwrite_id(session, appwrite_user_id)
    if existing is not None:
        _sync_email(session, existing, normalized)
        session.flush()
        return existing

    try:
        with session.begin_nested():
            user = User(
                appwrite_user_id=appwrite_user_id,
                email=normalized,
                onboarding_completed=False,
            )
            session.add(user)
            session.flush()
            return user
    except IntegrityError:
        # Either a concurrent first login won the appwrite_user_id race
        # (re-read the winner below) or a different identity owns this
        # email (never merge -> conflict).
        existing = _find_by_appwrite_id(session, appwrite_user_id)
        if existing is not None:
            _sync_email(session, existing, normalized)
            session.flush()
            return existing
        raise conflict(
            "That email address is already associated with another account."
        ) from None


def update_profile(
    session: Session,
    *,
    user_id: UUID,
    name: str,
    date_of_birth: date,
) -> User | None:
    """Store the validated profile; onboarding completion is server-derived.

    ``name``/``date_of_birth`` arrive already validated by ``ProfileUpdateRequest``
    (non-blank name <= 150 chars, DOB not in the future); both are required,
    so a successful update always completes onboarding.  Nothing else on the
    row ( ``id``, ``appwrite_user_id``, ``email``) is client-settable.
    """
    user = session.get(User, user_id)
    if user is None:
        return None
    user.name = name
    user.date_of_birth = date_of_birth
    user.onboarding_completed = derive_onboarding_completed(name, date_of_birth)
    session.flush()
    return user


__all__ = [
    "bootstrap_user",
    "get_user",
    "normalize_email",
    "update_profile",
]

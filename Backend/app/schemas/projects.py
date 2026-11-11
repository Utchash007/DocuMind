"""Project DTOs: ``/projects``."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import CamelModel, RequestModel


def _strip(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("value must not be blank")
    return stripped


class Project(CamelModel):
    id: UUID
    name: str
    description: str | None = None
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ProjectCreateRequest(RequestModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)

    @field_validator("name")
    @classmethod
    def _name(cls, value: str) -> str:
        checked = _strip(value)
        if len(checked) > 255:
            raise ValueError("name must be at most 255 characters")
        return checked

    @field_validator("description")
    @classmethod
    def _description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        # A blank description is normalized to "no description".
        return stripped or None


class ProjectUpdateRequest(RequestModel):
    """``PATCH /projects/{id}``: at least one field must be provided."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def _name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        checked = _strip(value)
        if len(checked) > 255:
            raise ValueError("name must be at most 255 characters")
        return checked

    @field_validator("description")
    @classmethod
    def _description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    def has_changes(self) -> bool:
        """True when the PATCH body carries at least one field."""
        return self.name is not None or self.description is not None


class ProjectDeleteAccepted(CamelModel):
    """``DELETE /projects/{id}`` -> 202 body while cleanup is pending.

    The project is tombstoned and hidden from reads immediately; the hard
    delete lands only after all child document cleanup jobs succeed.
    """

    project_id: UUID
    accepted: bool = True


__all__ = [
    "Project",
    "ProjectCreateRequest",
    "ProjectDeleteAccepted",
    "ProjectUpdateRequest",
]

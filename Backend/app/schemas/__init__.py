"""Public DTO surface for the NoteMind v2 API.

Consumers import from here or from the submodules; the wire shape is
camelCase (`model_dump(by_alias=True)`), Python names are snake_case.
"""

from app.schemas.common import (
    ApiError,
    Citation,
    CursorPageParams,
    DocumentStatus,
    ErrorCode,
    ErrorEnvelope,
    GenerationStatus,
    JobKind,
    JobStage,
    JobStatus,
    MessageRole,
    PaginatedResponse,
    decode_cursor,
    encode_cursor,
)
from app.schemas.conversations import (
    Conversation,
    ConversationCreateRequest,
    ConversationDeleteAccepted,
    ConversationUpdateRequest,
)
from app.schemas.documents import Document, DocumentDeleteAccepted, UploadAcceptance
from app.schemas.jobs import ProcessingJob
from app.schemas.messages import (
    Message,
    MessageCancelResponse,
    MessageCreateRequest,
    MessageRetryRequest,
    TurnResponse,
)
from app.schemas.projects import (
    Project,
    ProjectCreateRequest,
    ProjectDeleteAccepted,
    ProjectUpdateRequest,
)
from app.schemas.users import ApplicationUser, AuthenticatedUser, ProfileUpdateRequest

__all__ = [
    "ApiError",
    "ApplicationUser",
    "AuthenticatedUser",
    "Citation",
    "Conversation",
    "ConversationCreateRequest",
    "ConversationDeleteAccepted",
    "ConversationUpdateRequest",
    "CursorPageParams",
    "Document",
    "DocumentDeleteAccepted",
    "DocumentStatus",
    "ErrorCode",
    "ErrorEnvelope",
    "GenerationStatus",
    "JobKind",
    "JobStage",
    "JobStatus",
    "Message",
    "MessageCancelResponse",
    "MessageCreateRequest",
    "MessageRetryRequest",
    "MessageRole",
    "PaginatedResponse",
    "ProcessingJob",
    "ProfileUpdateRequest",
    "Project",
    "ProjectCreateRequest",
    "ProjectDeleteAccepted",
    "ProjectUpdateRequest",
    "TurnResponse",
    "UploadAcceptance",
    "decode_cursor",
    "encode_cursor",
]

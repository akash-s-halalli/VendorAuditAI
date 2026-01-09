"""Pydantic schemas package."""

from app.schemas.auth import (
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    PasswordChange,
    TokenResponse,
    TokenRefresh,
    OrganizationBase,
    OrganizationResponse,
    RegisterResponse,
)
from app.schemas.vendor import (
    VendorBase,
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorListResponse,
)
from app.schemas.document import (
    DocumentBase,
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
)
from app.schemas.chunk import (
    ChunkResponse,
    ChunkListResponse,
    SearchQuery,
    SearchResultResponse,
    SearchResponse,
)
from app.schemas.finding import (
    AnalysisRequest,
    AnalysisRunResponse,
    AnalysisRunListResponse,
    FindingResponse,
    FindingListResponse,
    FindingUpdate,
    FindingSummary,
)
from app.schemas.query import (
    QueryRequest,
    QueryResponse,
    ConversationRequest,
    ConversationResponse,
    ConversationCreateRequest,
    ConversationMessage,
    QueryHistoryResponse,
    QueryHistoryListResponse,
    ConversationListResponse,
    Citation,
)

__all__ = [
    # Auth
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "PasswordChange",
    "TokenResponse",
    "TokenRefresh",
    "OrganizationBase",
    "OrganizationResponse",
    "RegisterResponse",
    # Vendor
    "VendorBase",
    "VendorCreate",
    "VendorUpdate",
    "VendorResponse",
    "VendorListResponse",
    # Document
    "DocumentBase",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentListResponse",
    # Chunk/Search
    "ChunkResponse",
    "ChunkListResponse",
    "SearchQuery",
    "SearchResultResponse",
    "SearchResponse",
    # Analysis/Findings
    "AnalysisRequest",
    "AnalysisRunResponse",
    "AnalysisRunListResponse",
    "FindingResponse",
    "FindingListResponse",
    "FindingUpdate",
    "FindingSummary",
    # Query
    "QueryRequest",
    "QueryResponse",
    "ConversationRequest",
    "ConversationResponse",
    "ConversationCreateRequest",
    "ConversationMessage",
    "QueryHistoryResponse",
    "QueryHistoryListResponse",
    "ConversationListResponse",
    "Citation",
]

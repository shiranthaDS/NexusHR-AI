from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "employee"  # employee, hr_manager, admin
    disabled: Optional[bool] = False


class UserInDB(User):
    hashed_password: str


class DocumentUpload(BaseModel):
    filename: str
    content_type: str
    size: int


class DocumentMetadata(BaseModel):
    document_type: str = "policy"  # policy, handbook, memo, etc.
    uploaded_by: str
    upload_date: datetime = Field(default_factory=datetime.now)
    version: Optional[str] = None
    tags: Optional[List[str]] = []


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The user's question")
    chat_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Previous chat messages for context"
    )
    include_sources: bool = Field(
        default=True,
        description="Whether to include source documents in response"
    )


class QueryResponse(BaseModel):
    status: str
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None
    question: str
    intent: Optional[str] = None
    suggestions: Optional[List[str]] = None


class IntentClassification(BaseModel):
    question: str
    intent: str  # "policy" or "personal_data"
    confidence: float = 0.0


class DocumentIngestionResponse(BaseModel):
    status: str
    message: str
    chunks_created: Optional[int] = None
    pages_processed: Optional[int] = None
    document_id: Optional[str] = None


class CollectionStats(BaseModel):
    status: str
    collection_name: str
    document_count: int
    embedding_model: str


class HealthCheck(BaseModel):
    status: str
    version: str
    rag_system_initialized: bool
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: Optional[str] = None

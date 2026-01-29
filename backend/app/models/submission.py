"""Pydantic models for submission data."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class SubmissionCreate(BaseModel):
    """Model for creating a new submission."""
    name: str
    email: EmailStr
    event_name: Optional[str] = None


class SubmissionResponse(BaseModel):
    """Model for submission response."""
    id: UUID
    name: str
    email: str
    event_name: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    beo_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    """Response model for file upload."""
    submission_id: UUID
    status: str
    status_url: str
    message: str

"""Status endpoint for checking submission progress."""
from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from typing import Optional

from app.models.submission import SubmissionResponse
from app.services.database import db_service
from app.core.config import settings

router = APIRouter()
security = HTTPBearer(auto_error=False)


def verify_api_key(credentials: HTTPAuthorizationCredentials):
    """Verify API key from Authorization header."""
    if credentials.credentials != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


@router.get("/status/{submission_id}", response_model=SubmissionResponse)
async def get_status(
    submission_id: UUID,
    authorization: Optional[HTTPAuthorizationCredentials] = security,
):
    """
    Get the status of a submission.
    Requires API key in Authorization header.
    """
    # Verify API key
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    verify_api_key(authorization)
    
    # Get submission from database
    submission = db_service.get_submission(submission_id)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return SubmissionResponse(**submission)

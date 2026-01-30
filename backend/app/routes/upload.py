"""File upload endpoint."""
import os
import tempfile
from datetime import datetime, timedelta
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict

from app.models.submission import SubmissionCreate, UploadResponse
from app.services.database import db_service
from app.services.pdf_processor import process_pdf_async
from app.core.config import settings

router = APIRouter()
security = HTTPBearer(auto_error=False)

# Simple in-memory rate limiting (for production, use Redis)
_rate_limit_store: Dict[str, list] = {}


def verify_api_key(credentials: HTTPAuthorizationCredentials):
    """Verify API key from Authorization header."""
    if credentials.credentials != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


def check_rate_limit(email: str) -> bool:
    """Check if email has exceeded rate limit."""
    now = datetime.utcnow()
    hour_ago = now - timedelta(hours=1)
    
    # Clean old entries
    if email in _rate_limit_store:
        _rate_limit_store[email] = [
            ts for ts in _rate_limit_store[email] if ts > hour_ago
        ]
    else:
        _rate_limit_store[email] = []
    
    # Check limit
    if len(_rate_limit_store[email]) >= settings.rate_limit_per_hour:
        return False
    
    # Add current request
    _rate_limit_store[email].append(now)
    return True


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    event_name: Optional[str] = Form(None),
    pdf_file: UploadFile = File(...),
):
    """
    Upload a PDF file for processing.
    Requires API key in Authorization header.
    """
    # Get authorization from header (not from form data)
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    # Extract Bearer token
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    token = auth_header.replace("Bearer ", "").strip()
    if token != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limit
    if not check_rate_limit(email):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {settings.rate_limit_per_hour} submissions per hour."
        )
    
    # Validate file type
    if not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Check MIME type
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Get file size
    file_size = 0
    temp_file_path = None
    
    try:
        # Save uploaded file to temporary location
        temp_dir = tempfile.mkdtemp(prefix="beo_upload_")
        temp_file_path = os.path.join(temp_dir, pdf_file.filename)
        
        with open(temp_file_path, "wb") as f:
            content = await pdf_file.read()
            file_size = len(content)
            f.write(content)
        
        # Validate file size if limit is set
        if settings.max_file_size_bytes:
            if file_size > settings.max_file_size_bytes:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum of {settings.max_file_size_mb}MB"
                )
        
        # Create submission record
        submission_id = db_service.create_submission(
            name=name,
            email=email,
            event_name=event_name,
            file_size=file_size,
        )
        
        # Queue background processing task
        background_tasks.add_task(
            process_pdf_async,
            submission_id=submission_id,
            pdf_file_path=temp_file_path,
            name=name,
            email=email,
            event_name=event_name,
        )
        
        return UploadResponse(
            submission_id=submission_id,
            status="pending",
            status_url=f"/api/status/{submission_id}",
            message="File uploaded successfully. Processing will begin shortly."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file on error
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

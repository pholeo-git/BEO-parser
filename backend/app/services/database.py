"""Supabase database client for submissions."""
from supabase import create_client, Client
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.core.config import settings


class DatabaseService:
    """Service for interacting with Supabase database."""
    
    def __init__(self):
        self.client: Client = create_client(settings.supabase_url, settings.supabase_service_key)
    
    def create_submission(
        self,
        name: str,
        email: str,
        event_name: Optional[str],
        file_size: int,
    ) -> UUID:
        """Create a new submission record."""
        result = self.client.table("submissions").insert({
            "name": name,
            "email": email,
            "event_name": event_name,
            "status": "pending",
            "file_size": file_size,
        }).execute()
        
        return UUID(result.data[0]["id"])
    
    def update_submission_status(
        self,
        submission_id: UUID,
        status: str,
        download_url: Optional[str] = None,
        error_message: Optional[str] = None,
        beo_count: Optional[int] = None,
    ):
        """Update submission status and related fields."""
        update_data = {
            "status": status,
        }
        
        if download_url:
            update_data["download_url"] = download_url
        if error_message:
            update_data["error_message"] = error_message
        if beo_count is not None:
            update_data["beo_count"] = beo_count
        if status in ["completed", "failed"]:
            update_data["completed_at"] = datetime.utcnow().isoformat()
        
        self.client.table("submissions").update(update_data).eq("id", str(submission_id)).execute()
    
    def get_submission(self, submission_id: UUID) -> Optional[dict]:
        """Get a submission by ID."""
        result = self.client.table("submissions").select("*").eq("id", str(submission_id)).execute()
        
        if result.data:
            return result.data[0]
        return None


# Singleton instance
db_service = DatabaseService()

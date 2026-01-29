"""Supabase Storage service for file uploads and signed URLs."""
from supabase import create_client, Client
from typing import Optional
from datetime import datetime, timedelta
import os

from app.core.config import settings


class StorageService:
    """Service for interacting with Supabase Storage."""
    
    def __init__(self):
        self.client: Client = create_client(settings.supabase_url, settings.supabase_service_key)
        self.bucket_name = settings.storage_bucket_name
    
    def upload_file(
        self,
        file_path: str,
        storage_path: str,
    ) -> bool:
        """Upload a file to Supabase Storage."""
        try:
            with open(file_path, "rb") as f:
                self.client.storage.from_(self.bucket_name).upload(
                    path=storage_path,
                    file=f,
                    file_options={"content-type": "application/zip"}
                )
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    def create_signed_url(
        self,
        storage_path: str,
        expires_in_days: Optional[int] = None,
    ) -> Optional[str]:
        """Create a signed URL for downloading a file."""
        if expires_in_days is None:
            expires_in_days = settings.download_url_expiry_days
        
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        expires_at_timestamp = int(expires_at.timestamp())
        
        try:
            result = self.client.storage.from_(self.bucket_name).create_signed_url(
                path=storage_path,
                expires_in=expires_in_days * 24 * 60 * 60,  # Convert days to seconds
            )
            return result.get("signedURL")
        except Exception as e:
            print(f"Error creating signed URL: {e}")
            return None
    
    def delete_file(self, storage_path: str) -> bool:
        """Delete a file from storage."""
        try:
            self.client.storage.from_(self.bucket_name).remove([storage_path])
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


# Singleton instance
storage_service = StorageService()

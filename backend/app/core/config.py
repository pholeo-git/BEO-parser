"""Configuration settings for the BEO Separator API."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_secret_key: str
    cors_origins: str = "http://localhost:3000"  # Comma-separated origins
    
    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    
    # Postmark Configuration
    postmark_api_key: str
    postmark_from_email: str
    
    # Storage Configuration
    storage_bucket_name: str = "beo-outputs"
    download_url_expiry_days: int = 30
    
    # Processing Configuration
    max_file_size_mb: Optional[int] = None  # None = no limit (set empty string in env for no limit)
    rate_limit_per_hour: int = 5
    
    @property
    def max_file_size_bytes(self) -> Optional[int]:
        """Get max file size in bytes."""
        if self.max_file_size_mb is None:
            return None
        return self.max_file_size_mb * 1024 * 1024
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

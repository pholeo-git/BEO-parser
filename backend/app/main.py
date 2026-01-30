"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from app.core.config import settings
from app.routes import upload, status

app = FastAPI(
    title="BEO Separator API",
    description="API for splitting BEO PDF packets into individual BEO files",
    version="1.0.0"
)

# Configure CORS
origins = [origin.strip() for origin in settings.cors_origins.split(",")]

def is_origin_allowed(origin: str) -> bool:
    """Check if origin is allowed (explicit list or vercel.app domain)."""
    if origin in origins:
        return True
    # Allow all vercel.app subdomains (for preview deployments)
    if origin.endswith('.vercel.app'):
        return True
    return False

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?|https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(status.router, prefix="/api", tags=["status"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "BEO Separator API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

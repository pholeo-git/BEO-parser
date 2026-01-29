"""PDF processing service for splitting BEOs."""
import os
import zipfile
import tempfile
import shutil
from typing import Tuple
from uuid import UUID

from app.core.beo_split import split_pdf
from app.services.database import db_service
from app.services.storage import storage_service
from app.services.email import email_service
from app.core.config import settings


async def process_pdf_async(
    submission_id: UUID,
    pdf_file_path: str,
    name: str,
    email: str,
    event_name: str = None,
) -> Tuple[bool, str]:
    """
    Process a PDF file asynchronously.
    Returns: (success, error_message)
    """
    temp_dir = None
    try:
        # Update status to processing
        db_service.update_submission_status(submission_id, "processing")
        
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp(prefix="beo_process_")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Process the PDF
        num_beos, problem_pages, report_path = split_pdf(
            input_pdf=pdf_file_path,
            outdir=output_dir,
            stop_on_problems=False,  # Don't stop, just log problems
        )
        
        # Create zip file
        zip_path = os.path.join(temp_dir, f"beos_{submission_id}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all BEO PDFs
            for file in os.listdir(output_dir):
                if file.endswith('.pdf') and file.startswith('BEO_'):
                    file_path = os.path.join(output_dir, file)
                    zipf.write(file_path, file)
            
            # Add split_report.csv
            if os.path.exists(report_path):
                zipf.write(report_path, "split_report.csv")
        
        # Upload zip to storage
        storage_path = f"submissions/{submission_id}/beos.zip"
        if not storage_service.upload_file(zip_path, storage_path):
            raise Exception("Failed to upload file to storage")
        
        # Generate signed URL
        download_url = storage_service.create_signed_url(
            storage_path,
            expires_in_days=settings.download_url_expiry_days
        )
        
        if not download_url:
            raise Exception("Failed to generate download URL")
        
        # Update database with results
        db_service.update_submission_status(
            submission_id,
            "completed",
            download_url=download_url,
            beo_count=num_beos,
        )
        
        # Send email
        email_service.send_download_link(
            to_email=email,
            to_name=name,
            event_name=event_name,
            download_url=download_url,
            beo_count=num_beos,
        )
        
        return True, ""
        
    except Exception as e:
        error_msg = str(e)
        db_service.update_submission_status(
            submission_id,
            "failed",
            error_message=error_msg,
        )
        return False, error_msg
        
    finally:
        # Clean up temporary files
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Clean up uploaded PDF
        if pdf_file_path and os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)

"""Postmark email service for sending download links."""
import requests
from typing import Optional

from app.core.config import settings


class EmailService:
    """Service for sending emails via Postmark."""
    
    def __init__(self):
        self.api_key = settings.postmark_api_key
        self.from_email = settings.postmark_from_email
        self.base_url = "https://api.postmarkapp.com"
    
    def send_download_link(
        self,
        to_email: str,
        to_name: str,
        event_name: Optional[str],
        download_url: str,
        beo_count: int,
    ) -> bool:
        """Send email with download link."""
        subject = f"Your BEO files are ready" + (f" - {event_name}" if event_name else "")
        
        event_text = f" for {event_name}" if event_name else ""
        body_html = f"""
        <html>
        <body style="font-family: 'Open Sans', Arial, sans-serif; color: #3f4040; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #045559; font-family: 'KoHo', Arial, sans-serif; font-weight: 500;">
                    Your BEO files are ready{event_text}
                </h1>
                <p>Hi {to_name},</p>
                <p>Your BEO packet has been processed successfully. We've created <strong>{beo_count} individual BEO file(s)</strong> for you.</p>
                <p>The download includes:</p>
                <ul>
                    <li>Individual BEO PDFs (BEO_&lt;NUMBER&gt;.pdf)</li>
                    <li>split_report.csv (page-by-page audit report)</li>
                </ul>
                <div style="margin: 30px 0; text-align: center;">
                    <a href="{download_url}" 
                       style="background-color: #e0893f; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 10px; display: inline-block; 
                              font-weight: bold;">
                        Download Your Files
                    </a>
                </div>
                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    <strong>Note:</strong> This download link will expire in {settings.download_url_expiry_days} days.
                </p>
                <p style="color: #666; font-size: 14px;">
                    If you have any questions, please don't hesitate to reach out.
                </p>
            </div>
        </body>
        </html>
        """
        
        body_text = f"""
        Hi {to_name},
        
        Your BEO packet has been processed successfully. We've created {beo_count} individual BEO file(s) for you.
        
        The download includes:
        - Individual BEO PDFs (BEO_<NUMBER>.pdf)
        - split_report.csv (page-by-page audit report)
        
        Download your files: {download_url}
        
        Note: This download link will expire in {settings.download_url_expiry_days} days.
        """
        
        return self._send_email(to_email, subject, body_text, body_html)
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: str,
    ) -> bool:
        """Send email via Postmark API."""
        url = f"{self.base_url}/email"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Postmark-Server-Token": self.api_key,
        }
        
        payload = {
            "From": self.from_email,
            "To": to_email,
            "Subject": subject,
            "TextBody": body_text,
            "HtmlBody": body_html,
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending email via Postmark: {e}")
            return False


# Singleton instance
email_service = EmailService()

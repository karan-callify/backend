# app/api/routes/v1/process_calls/services.py

from typing import Optional, Literal
from app.utils.process_call_convo import process_convocall
from app.utils.process_convo_call_email import process_convocall_email

from app.utils.logger_util import logger


class ProcessCallService:
    """Service for processing convocall requests."""
    
    def __init__(self):
        pass
    
    async def process_convocall_request(
        self,
        transcript_text: Optional[str],
        jdfile_name: Optional[str],
        env: str,
        vendor_id: str = "1",
        intent_id: str = "1",
        language_code: Literal["en", "pt","es"] = "en"
    ) -> dict:
        """
        Process a convocall request and generate call flow script.
        
        Args:
            transcript_text: Transcript or context text
            jdfile_name: Job description file name (if uploaded)
            env: Environment (dev/prod)
            vendor_id: Vendor identifier
            intent_id: Intent identifier
            language_code: Language code for output
        
        Returns:
            Dictionary containing the generated call flow
        """
        try:
            result = process_convocall(
                transcript_text=transcript_text,
                jdfile=jdfile_name,
                env=env,
                vendor_id=vendor_id,
                intent_id=intent_id,
                language_code=language_code
            )
            
            return {
                "success": True,
                "data": result
            }
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Service error: {e}")
            return {
                "success": False,
                "error": "An error occurred while processing the request"
            }


class ProcessEmailService:
    """Service for processing convocall email requests."""

    def __init__(self):
        pass

    async def process_convocall_email_request(
        self,
        transcript_text: Optional[str],
        jdfile_name: Optional[str],
        env: str,
        vendor_id: str = "1",
        intent_id: str = "1",
        language_code: Literal["en", "pt", "es"] = "en"
    ) -> dict:
        """
        Process a convocall email request and generate email content.
        """
        try:
            result = process_convocall_email(
                transcript_text=transcript_text,
                jdfile=jdfile_name,
                env=env,
                vendor_id=vendor_id,
                intent_id=intent_id,
                language_code=language_code
            )
            return {
                "success": True,
                "data": result
            }
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Service error: {e}")
            return {
                "success": False,
                "error": "An error occurred while processing the email request"
            }
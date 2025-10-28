# app/api/routes/dependencies.py

from typing import Annotated
from fastapi import Depends

from app.service.process_call_and_email import ProcessCallService, ProcessEmailService

# Service Dependency
def get_process_call_service() -> ProcessCallService:
    """
    Dependency injection for ProcessCallService.
    Returns a new instance of the service for each request.
    """
    return ProcessCallService()

def get_process_email_service() -> ProcessEmailService:
    """
    Dependency injection for ProcessEmailService.
    Returns a new instance of the service for each request.
    """
    return ProcessEmailService()

# Type alias for dependency injection
ProcessCallServiceDep = Annotated[ProcessCallService, Depends(get_process_call_service)]
ProcessEmailServiceDep = Annotated[ProcessEmailService, Depends(get_process_email_service)]
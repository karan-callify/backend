# app/api/routes/v1/process_calls/routes.py

from typing import Optional
import os
import uuid
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from app.utils.logger_util import logger
from app.schemas.process_call_and_email import (
    ProcessConvocallForm,
    ProcessConvocallEmailForm,
    ProcessConvocallResponse,
    ProcessConvocallEmailResponse,
)
from app.dependencies import ProcessCallServiceDep, ProcessEmailServiceDep

router = APIRouter()


@router.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"message": "API is running"}


@router.post("/convocall", response_model=ProcessConvocallResponse)
async def create_convocall(
    service: ProcessCallServiceDep,
    data: tuple[ProcessConvocallForm, Optional[UploadFile]] = Depends(ProcessConvocallForm.as_form)
):
    form_data, jdfile = data
    logger.info("Convocall API hit")
    logger.info(f"Received Convocall request with data: {form_data.model_dump()}")

    jdfile_name = None
    file_path = None

    # Handle uploaded file if present
    if jdfile:
        filename = jdfile.filename or ""
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)

        try:
            with open(file_path, "wb") as buffer:
                content = await jdfile.read()
                buffer.write(content)
            jdfile_name = unique_filename
            logger.info(f"Uploaded JD file saved as: {jdfile_name}")
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save uploaded file: {str(e)}"
            )

    # Process the Convocall request
    try:
        result = await service.process_convocall_request(
            transcript_text=form_data.transcript_text,
            jdfile_name=jdfile_name,
            env=form_data.env,
            vendor_id=form_data.vendor_id,
            intent_id=form_data.intent_id,
            language_code=form_data.language_code,
        )

        if not result.get("success"):
            logger.error(f"Convocall processing failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to process request"),
            )

        logger.info("Convocall processed successfully")
        return result["data"]

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Internal server error during Convocall: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Temporary file deleted: {jdfile_name}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {file_path}: {e}")


@router.post("/convocall-email", response_model=ProcessConvocallEmailResponse)
async def create_convocall_email(
    service: ProcessEmailServiceDep,
    data: tuple[ProcessConvocallEmailForm, Optional[UploadFile]] = Depends(ProcessConvocallEmailForm.as_form)
):
    form_data, jdfile = data
    logger.info("Convocall-email API hit")
    logger.info(f"Received Convocall-email request with data: {form_data.model_dump()}")

    jdfile_name = None
    file_path = None

    # Handle uploaded file if present
    if jdfile:
        filename = jdfile.filename or ""
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)

        try:
            with open(file_path, "wb") as buffer:
                content = await jdfile.read()
                buffer.write(content)
            jdfile_name = unique_filename
            logger.info(f"Uploaded JD file saved as: {jdfile_name}")
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save uploaded file: {str(e)}"
            )

    # Process the Convocall-email request
    try:
        result = await service.process_convocall_email_request(
            transcript_text=form_data.transcript_text,
            jdfile_name=jdfile_name,
            env=form_data.env,
            vendor_id=form_data.vendor_id,
            intent_id=form_data.intent_id,
            language_code=form_data.language_code,
        )

        if not result.get("success"):
            logger.error(f"Convocall-email failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to process request"),
            )

        logger.info("Convocall-email processed successfully")
        return result["data"]

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Internal server error during Convocall-email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Temporary file deleted: {jdfile_name}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {file_path}: {e}")

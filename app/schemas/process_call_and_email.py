from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, Union
from fastapi import Form, File, UploadFile

# ----------------------------------------
# 📹 Profile
# ----------------------------------------

class ProcessConvocallForm(BaseModel):
    job_id: Optional[str] = None
    transcript_text: str
    env: str
    vendor_id: str = "1"
    intent_id: str = "1"
    language_code: Literal["en", "pt","es"] = "en"

    @classmethod
    def as_form(
        cls,
        job_id: Optional[str] = Form(None),
        transcript_text: str = Form(...),
        env: str = Form(...),
        vendor_id: str = Form("1"),
        intent_id: str = Form("1"),
        language_code: Literal["en", "pt","es"] = Form("en"),
        jdfile: Union[UploadFile, str, None] = File(None),
    ) -> tuple["ProcessConvocallForm", Optional[UploadFile]]:
        # Handle cases where jdfile is sent as empty str (e.g., in urlencoded requests)
        if isinstance(jdfile, str):
            jdfile = None
        
        # Handle empty file uploads (e.g., filename="" in multipart requests)
        if jdfile and hasattr(jdfile, 'filename'):
            if jdfile.filename == "":
                jdfile = None
            
        return (
            cls(
                job_id=job_id,
                transcript_text=transcript_text,
                env=env,
                vendor_id=vendor_id,
                intent_id=intent_id,
                language_code=language_code,
            ),
            jdfile,
        )

class ProcessConvocallEmailForm(BaseModel):
    job_id: Optional[str] = None
    transcript_text: str
    env: str
    vendor_id: str = "1"
    intent_id: str = "1"
    language_code: Literal["en", "pt", "es"] = "en"

    @classmethod
    def as_form(
        cls,
        job_id: Optional[str] = Form(None),
        transcript_text: str = Form(...),
        env: str = Form(...),
        vendor_id: str = Form("1"),
        intent_id: str = Form("1"),
        language_code: Literal["en", "pt", "es"] = Form("en"),
        jdfile: Union[UploadFile, str, None] = File(None),
    ) -> tuple["ProcessConvocallEmailForm", Optional[UploadFile]]:
        # Handle cases where jdfile is sent as empty str (e.g., in urlencoded requests)
        if isinstance(jdfile, str):
            jdfile = None
        
        # Handle empty file uploads (e.g., filename="" in multipart requests)
        if jdfile and hasattr(jdfile, 'filename'):
            if jdfile.filename == "":
                jdfile = None
            
        return (
            cls(
                job_id=job_id,
                transcript_text=transcript_text,
                env=env,
                vendor_id=vendor_id,
                intent_id=intent_id,
                language_code=language_code,
            ),
            jdfile,
        )

class PreScreeningQuestion(BaseModel):
    question: str = Field(..., alias="Question")
    ideal_answer: str = Field(..., alias="Ideal Answer")

    model_config = {"populate_by_name": True}


class ProcessConvocallResponse(BaseModel):
    prompt: str = Field(..., alias="Prompt")
    opening_layer: str = Field(..., alias="Opening Layer")
    context_of_the_call: str = Field(..., alias="Context of the Call")
    job_overview: str = Field(..., alias="Job Overview")
    pre_screening_questions: list[PreScreeningQuestion] = Field(..., alias="Pre-screening Questions")
    call_ending_message: str = Field(..., alias="Call Ending Message")

    model_config = {"populate_by_name": True}

class ProcessConvocallEmailResponse(BaseModel):
    subject: str
    body: str

    model_config = {"populate_by_name": True}
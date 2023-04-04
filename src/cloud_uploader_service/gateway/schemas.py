from typing import Optional
from uuid import UUID
from pydantic import BaseModel, validator


class ResponseModel(BaseModel):
    status: str = 'SUCCESS'
    data: dict = dict()
    exc_code: Optional[str] = None
    exc_data: Optional[str] = None
    message: Optional[str] = None


class CreateUploadCaseData(BaseModel):
    part_amount: int


class UploadFilePartData(BaseModel):
    reference: UUID
    upload_part_bytes: bytes
    upload_part_number: int

    @validator('upload_part_bytes', pre=True)
    def _validate_bytes(cls, v):
        v = v.encode('cp437')
        return v


class CompleteUploadData(BaseModel):
    reference: UUID


class DeleteUploadData(BaseModel):
    reference: UUID

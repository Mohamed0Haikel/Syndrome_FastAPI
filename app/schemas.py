# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import List, Optional

# Doctor Schemas
class DoctorBase(BaseModel):
    name: str
    email: EmailStr

class DoctorCreate(DoctorBase):
    password: str

class DoctorResponse(DoctorBase):
    id: int

    class Config:
        orm_mode = True

# Patient Schemas
class PatientBase(BaseModel):
    name: str

class PatientCreate(PatientBase):
    doctor_id: int

class PatientResponse(PatientBase):
    id: int
    doctor: DoctorResponse

    class Config:
        orm_mode = True

# Case Schemas
class CaseBase(BaseModel):
    description: str

class CaseCreate(CaseBase):
    patient_id: int

class CaseResponse(CaseBase):
    id: int
    patient: PatientResponse

    class Config:
        orm_mode = True

# SyndromeDetection Schemas
class SyndromeDetectionBase(BaseModel):
    syndrome_name: str

class SyndromeDetectionCreate(SyndromeDetectionBase):
    patient_id: int

class SyndromeDetectionResponse(SyndromeDetectionBase):
    id: int
    patient: PatientResponse

    class Config:
        orm_mode = True

# PatientNote Schemas
class PatientNoteBase(BaseModel):
    note: str

class PatientNoteCreate(PatientNoteBase):
    patient_id: int

class PatientNoteResponse(PatientNoteBase):
    id: int
    patient: PatientResponse

    class Config:
        orm_mode = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

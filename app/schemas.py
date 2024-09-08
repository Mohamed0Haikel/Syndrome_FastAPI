# app/schemas.py

from typing import List, Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenWithUserType(Token):
    user_type: str

class TokenData(BaseModel):
    email: str

class DoctorBase(BaseModel):
    name: str
    email: str

class DoctorCreate(DoctorBase):
    password: str

class DoctorResponse(DoctorBase):
    id: int

    class Config:
        from_attributes = True

class NormalUserBase(BaseModel):
    name: str
    email: str

class NormalUserCreate(NormalUserBase):
    password: str

class NormalUserResponse(NormalUserBase):
    id: int

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str

class PatientBase(BaseModel):
    name: str
    doctor_id: int

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int

    class Config:
        from_attributes = True

class CaseBase(BaseModel):
    description: str
    patient_id: int

class CaseCreate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: int

    class Config:
        from_attributes = True

class SyndromeDetectionBase(BaseModel):
    syndrome_name: str
    patient_id: int

class SyndromeDetectionCreate(SyndromeDetectionBase):
    pass

class SyndromeDetectionResponse(SyndromeDetectionBase):
    id: int
    normal_user_id: Optional[int]

    class Config:
        from_attributes = True

class PatientNoteBase(BaseModel):
    note: str
    patient_id: int

class PatientNoteCreate(PatientNoteBase):
    pass

class PatientNoteResponse(PatientNoteBase):
    id: int

    class Config:
        from_attributes = True

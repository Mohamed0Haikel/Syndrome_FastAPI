# app/schemas.py

from typing import List, Optional
from pydantic import BaseModel

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Admin Schemas
class AdminBase(BaseModel):
    name: str
    email: str

class AdminCreate(AdminBase):
    password: str

class AdminResponse(AdminBase):
    id: int

    class Config:
        from_attributes = True

# Doctor Schemas
class DoctorBase(BaseModel):
    name: str
    email: str

class DoctorCreate(DoctorBase):
    password: str

class DoctorResponse(DoctorBase):
    id: int

    class Config:
        from_attributes = True

# Normal User Schemas
class NormalUserBase(BaseModel):
    name: str
    email: str

class NormalUserCreate(NormalUserBase):
    password: str

class NormalUserResponse(NormalUserBase):
    id: int
    profile_data: Optional[str]

    class Config:
        from_attributes = True

# Case and Detection Schemas
class CaseBase(BaseModel):
    description: str
    doctor_id: int

class CaseCreate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: int

    class Config:
        from_attributes = True

class SyndromeDetectionBase(BaseModel):
    result: str
    image_url: str

class SyndromeDetectionCreate(SyndromeDetectionBase):
    case_id: Optional[int]
    normal_user_id: Optional[int]

class SyndromeDetectionResponse(SyndromeDetectionBase):
    id: int

    class Config:
        from_attributes = True

# Article Schemas
class ArticleBase(BaseModel):
    title: str
    author: str
    photo_url: str
    content: str

class ArticleCreate(ArticleBase):
    pass

class ArticleResponse(ArticleBase):
    id: int

    class Config:
        from_attributes = True


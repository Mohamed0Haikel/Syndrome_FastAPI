# app/schemas.py

from typing import List, Optional
from pydantic import BaseModel


# class GenericResponse(BaseModel):
#     message: str
class GenericResponse(BaseModel):
    success: bool
    message: str

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int
    user_data: Optional[dict] = None



class LoginRequest(BaseModel):
    email: str
    password: str


class TokenData(BaseModel):
    email: str
    user_type: str
    user_id: int


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
    phone: str
    email: str


class DoctorCreate(DoctorBase):
    password: str


class DoctorResponse(DoctorBase):
    id: int
    name: str
    phone: str
    email: str
    profile_image: str

    class Config:
        from_attributes = True


# Normal User Schemas
class NormalUserBase(BaseModel):
    name: str
    phone: str
    email: str




class NormalUserCreate(NormalUserBase):
    password: str


class NormalUserResponse(NormalUserBase):
    id: int
    name: str
    phone: str
    email: str
    profile_image: str


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


class SyndromeDetectionCreate(BaseModel):
    result: str
    image_url: str
    date_of_detection: str
    case_id: Optional[int] = None
    normal_user_id: Optional[int] = None
    # User-specific attributes
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    description: Optional[str] = None

    @staticmethod
    def validate_detection(data: dict):
        if data.get("case_id") and data.get("normal_user_id"):
            raise ValueError("Both case_id and normal_user_id cannot be provided.")
        if not data.get("case_id") and not data.get("normal_user_id"):
            raise ValueError("Either case_id or normal_user_id must be provided.")
        if data.get("case_id"):
            required_fields = ["description"]
        else:
            required_fields = ["name", "age", "gender", "nationality", "description"]
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing fields for detection: {', '.join(missing)}")


class SyndromeDetectionResponse(BaseModel):
    id: int
    result: str
    image_url: str
    date_of_detection: str
    case_id: Optional[int] = None
    normal_user_id: Optional[int] = None
    # User-specific attributes
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

# Article Schemas
class ArticleBase(BaseModel):
    id: int
    title: str
    author: str
    photo_url: str
    content: str


class ArticleCreate(BaseModel):
    title: str
    author: str
    content: str

class ArticleResponse(ArticleBase):
    id: int

    class Config:
        from_attributes = True

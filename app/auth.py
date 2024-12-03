# app/auth.py

import os
from datetime import datetime, timedelta
from typing import Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from . import schemas, models, crud
from .database import SessionLocal
from sqlalchemy.orm import Session

# Load environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str) -> Optional[Union[models.Admin, models.Doctor, models.NormalUser]]:
    user = crud.get_admin_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return user
    user = crud.get_doctor_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return user
    user = crud.get_normal_user_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def get_current_user(db: Session = Depends(SessionLocal), token: str = Depends(oauth2_scheme)) -> Union[models.Admin, models.Doctor, models.NormalUser]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        user_id: int = payload.get("user_id")
        if email is None or user_type is None or user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email, user_type=user_type, user_id=user_id)
    except JWTError:
        raise credentials_exception

    if user_type == "admin":
        user = crud.get_admin_by_email(db, email)
    elif user_type == "doctor":
        user = crud.get_doctor_by_email(db, email)
    elif user_type == "normal_user":
        user = crud.get_normal_user_by_email(db, email)
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return user

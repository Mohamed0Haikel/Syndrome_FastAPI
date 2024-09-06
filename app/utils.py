# app/utils.py

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from .database import SessionLocal
from .models import Doctor

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_doctor_ownership(doctor: Doctor, resource_doctor_id: int):
    if doctor.id != resource_doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted."
        )

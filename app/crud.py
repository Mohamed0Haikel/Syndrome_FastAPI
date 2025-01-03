# app/crud.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from . import models, schemas
from .auth import get_password_hash

import os
from fastapi import UploadFile
from uuid import uuid4


# Admin CRUD
def create_admin(db: Session, admin: schemas.AdminCreate) -> models.Admin:
    hashed_password = get_password_hash(admin.password)
    db_admin = models.Admin(
        name=admin.name,
        email=admin.email,
        hashed_password=hashed_password
    )
    try:
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        return db_admin
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered.")


def get_admin_by_email(db: Session, email: str) -> Optional[models.Admin]:
    return db.query(models.Admin).filter(models.Admin.email == email).first()


def get_all_admins(db: Session) -> List[models.Admin]:
    return db.query(models.Admin).all()


# Doctor CRUD
def create_doctor(db: Session, doctor: schemas.DoctorCreate, profile_image: UploadFile) -> models.Doctor:
    hashed_password = get_password_hash(doctor.password)

    # Save the uploaded file
    if not profile_image:
        raise HTTPException(status_code=400, detail="Image file is required.")

    file_extension = os.path.splitext(profile_image.filename)[1]
    if file_extension.lower() not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Supported formats: .jpg, .jpeg, .png")
    
    # Generate a unique filename and save the file
    unique_filename = f"{uuid4().hex}{file_extension}"
    file_path = os.path.join("media/users", unique_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as buffer:
        buffer.write(profile_image.file.read())

    db_doctor = models.Doctor(
        name=doctor.name,
        phone=doctor.phone,
        email=doctor.email,
        profile_image=f"/media/users/{unique_filename}",  # Save the URL to the
        hashed_password=hashed_password
    )
    try:
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered.")


def get_doctor_by_email(db: Session, email: str) -> Optional[models.Doctor]:
    return db.query(models.Doctor).filter(models.Doctor.email == email).first()


def get_all_doctors(db: Session) -> List[models.Doctor]:
    return db.query(models.Doctor).all()


# Normal User CRUD
def create_normal_user(db: Session, user: schemas.NormalUserCreate, profile_image: UploadFile) -> models.NormalUser:
    hashed_password = get_password_hash(user.password)
    # Save the uploaded file
    if not profile_image:
        raise HTTPException(status_code=400, detail="Image file is required.")

    file_extension = os.path.splitext(profile_image.filename)[1]
    if file_extension.lower() not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Supported formats: .jpg, .jpeg, .png")
    
    # Generate a unique filename and save the file
    unique_filename = f"{uuid4().hex}{file_extension}"
    file_path = os.path.join("media/users", unique_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as buffer:
        buffer.write(profile_image.file.read())

    db_user = models.NormalUser(
        name=user.name,
        phone=user.phone,
        email=user.email,
        profile_image=f"/media/users/{unique_filename}",  # Save the URL to the
        hashed_password=hashed_password
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered.")


def get_normal_user_by_email(db: Session, email: str) -> Optional[models.NormalUser]:
    return db.query(models.NormalUser).filter(models.NormalUser.email == email).first()


def get_all_normal_users(db: Session) -> List[models.NormalUser]:
    return db.query(models.NormalUser).all()


# Case CRUD
def create_case(db: Session, case: schemas.CaseCreate) -> models.Case:
    db_case = models.Case(
        description=case.description,
        doctor_id=case.doctor_id,
        name=case.name,
        age=case.age,
        gender=case.gender,
        nationality=case.nationality
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


def get_cases_by_doctor(db: Session, doctor_id: int) -> List[models.Case]:
    return db.query(models.Case).filter(models.Case.doctor_id == doctor_id).all()


def get_case_by_id(db: Session, case_id: int) -> Optional[models.Case]:
    return db.query(models.Case).filter(models.Case.id == case_id).first()


# Syndrome Detection CRUD
def create_syndrome_detection(db: Session, detection: schemas.SyndromeDetectionCreate, image_file: UploadFile) -> models.SyndromeDetection:
    # Validate input fields based on user or doctor case
    if detection.case_id and detection.normal_user_id:
        raise ValueError("Both case_id and normal_user_id cannot be provided.")
    if not detection.case_id and not detection.normal_user_id:
        raise ValueError("Either case_id or normal_user_id must be provided.")
    
    # Check required fields for each case type
    if detection.case_id:
        # Doctor case
        if not detection.description:
            raise ValueError("Description is required for doctor case detections.")
        # Exclude normal user-specific fields
        detection_data = detection.dict(exclude={"normal_user_id", "name", "age", "gender", "nationality"})
    else:
        # User case
        required_fields = ["name", "age", "gender", "nationality", "description"]
        missing_fields = [field for field in required_fields if getattr(detection, field, None) is None]
        if missing_fields:
            raise ValueError(f"Missing fields for user detection: {', '.join(missing_fields)}")
        # Exclude doctor-specific fields
        detection_data = detection.dict(exclude={"case_id"})

    # Save the uploaded file
    if not image_file:
        raise HTTPException(status_code=400, detail="Image file is required.")

    file_extension = os.path.splitext(image_file.filename)[1]
    if file_extension.lower() not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Supported formats: .jpg, .jpeg, .png")
    
    # Generate a unique filename and save the file
    unique_filename = f"{uuid4().hex}{file_extension}"
    file_path = os.path.join("media/detections", unique_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as buffer:
        buffer.write(image_file.file.read())

    # Add the image URL to detection data
    detection_data["image_url"] = f"/media/detections/{unique_filename}"

    # Create and save the detection
    db_detection = models.SyndromeDetection(**detection_data)
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection

def get_detections_by_case(db: Session, case_id: int) -> List[models.SyndromeDetection]:
    return db.query(models.SyndromeDetection).filter(models.SyndromeDetection.case_id == case_id).all()


def get_detections_by_user(db: Session, user_id: int) -> List[models.SyndromeDetection]:
    return db.query(models.SyndromeDetection).filter(models.SyndromeDetection.normal_user_id == user_id).all()


def get_detection_history_for_case(db: Session, case_id: int) -> List[models.SyndromeDetection]:
    return db.query(models.SyndromeDetection).filter(models.SyndromeDetection.case_id == case_id).all()


# Article CRUD
def create_article(db: Session, article: schemas.ArticleCreate, photo: UploadFile) -> models.Article:
    # Save the uploaded file
    if not photo:
        raise HTTPException(status_code=400, detail="Image file is required.")

    file_extension = os.path.splitext(photo.filename)[1]
    if file_extension.lower() not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Supported formats: .jpg, .jpeg, .png")
    
    # Generate a unique filename and save the file
    unique_filename = f"{uuid4().hex}{file_extension}"
    file_path = os.path.join("media/articles", unique_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as buffer:
        buffer.write(photo.file.read())

    # Save the article record with the photo URL
    db_article = models.Article(
        title=article.title,
        author=article.author,
        photo_url=f"/media/articles/{unique_filename}",  # Save the URL to the file
        content=article.content
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def get_articles(db: Session) -> List[models.Article]:
    return db.query(models.Article).order_by(models.Article.id.desc()).all()

# Add the delete_article function
def delete_article(db: Session, article_id: int) -> bool:
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if article:
        # Optionally delete the file from the filesystem
        if os.path.exists(article.photo_url):
            os.remove(article.photo_url)
        db.delete(article)
        db.commit()
        return True
    raise HTTPException(status_code=404, detail="Article not found.")
    # return True  # Return True if deletion is successful

# User Deletion
def delete_user(db: Session, user_id: int) -> None:
    user = db.query(models.NormalUser).filter(models.NormalUser.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return
    user = db.query(models.Doctor).filter(models.Doctor.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return
    user = db.query(models.Admin).filter(models.Admin.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return
    raise HTTPException(status_code=404, detail="User not found.")



def get_normal_user_by_id(db: Session, user_id: int):
    return db.query(models.NormalUser).filter(models.NormalUser.id == user_id).first()

def delete_normal_user(db: Session, user_id: int):
    user = get_normal_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()

def get_doctor_by_id(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def delete_doctor(db: Session, doctor_id: int):
    doctor = get_doctor_by_id(db, doctor_id)
    if doctor:
        db.delete(doctor)
        db.commit()
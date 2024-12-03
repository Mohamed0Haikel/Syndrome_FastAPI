# app/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import schemas, models, crud, auth, utils

router = APIRouter()

# Dependency
db_dependency = Depends(utils.get_db)

# --------------------------------------
# Admin Endpoints
# --------------------------------------

@router.post("/admin/register", response_model=schemas.AdminResponse)
def register_admin(admin: schemas.AdminCreate, db: Session = db_dependency):
    return crud.create_admin(db, admin)

@router.get("/admin/articles", response_model=List[schemas.ArticleResponse])
def get_all_articles(db: Session = db_dependency):
    return crud.get_articles(db)

@router.post("/admin/articles", response_model=schemas.ArticleResponse)
def create_article(article: schemas.ArticleCreate, db: Session = db_dependency):
    return crud.create_article(db, article)

@router.delete("/admin/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = db_dependency):
    user = db.query(models.NormalUser).filter(models.NormalUser.id == user_id).first() \
           or db.query(models.Doctor).filter(models.Doctor.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()

# --------------------------------------
# Doctor Endpoints
# --------------------------------------

@router.post("/doctor/register", response_model=schemas.DoctorResponse)
def register_doctor(doctor: schemas.DoctorCreate, db: Session = db_dependency):
    return crud.create_doctor(db, doctor)

@router.post("/doctor/cases", response_model=schemas.CaseResponse)
def create_case(case: schemas.CaseCreate, db: Session = db_dependency):
    return crud.create_case(db, case)

@router.get("/doctor/cases/{doctor_id}", response_model=List[schemas.CaseResponse])
def get_cases_for_doctor(doctor_id: int, db: Session = db_dependency):
    cases = db.query(models.Case).filter(models.Case.doctor_id == doctor_id).all()
    if not cases:
        raise HTTPException(status_code=404, detail="No cases found.")
    return cases

@router.post("/doctor/detections", response_model=schemas.SyndromeDetectionResponse)
def create_detection_for_case(detection: schemas.SyndromeDetectionCreate, db: Session = db_dependency):
    if not detection.case_id:
        raise HTTPException(status_code=400, detail="Case ID is required for doctor detections.")
    return crud.create_detection(db, detection)

@router.get("/doctor/detections/{case_id}", response_model=List[schemas.SyndromeDetectionResponse])
def get_detections_for_case(case_id: int, db: Session = db_dependency):
    detections = db.query(models.SyndromeDetection).filter(models.SyndromeDetection.case_id == case_id).all()
    if not detections:
        raise HTTPException(status_code=404, detail="No detections found for this case.")
    return detections

# --------------------------------------
# Normal User Endpoints
# --------------------------------------

@router.post("/user/register", response_model=schemas.NormalUserResponse)
def register_user(user: schemas.NormalUserCreate, db: Session = db_dependency):
    return crud.create_normal_user(db, user)

@router.post("/user/detections", response_model=schemas.SyndromeDetectionResponse)
def create_detection_for_user(detection: schemas.SyndromeDetectionCreate, db: Session = db_dependency):
    if not detection.normal_user_id:
        raise HTTPException(status_code=400, detail="User ID is required for user detections.")
    return crud.create_detection(db, detection)

@router.get("/user/detections/{user_id}", response_model=List[schemas.SyndromeDetectionResponse])
def get_detections_for_user(user_id: int, db: Session = db_dependency):
    detections = db.query(models.SyndromeDetection).filter(models.SyndromeDetection.normal_user_id == user_id).all()
    if not detections:
        raise HTTPException(status_code=404, detail="No detections found for this user.")
    return detections

@router.get("/user/profile/{user_id}", response_model=schemas.NormalUserResponse)
def get_user_profile(user_id: int, db: Session = db_dependency):
    user = db.query(models.NormalUser).filter(models.NormalUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

# app/routes.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, models, crud, auth, utils

router = APIRouter()

# Authentication Routes
@router.post("/auth/register_doctor", response_model=schemas.DoctorResponse)
def register_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(utils.get_db)):
    return crud.create_doctor(db, doctor)

@router.post("/auth/register_normal_user", response_model=schemas.NormalUserResponse)
def register_normal_user(user: schemas.NormalUserCreate, db: Session = Depends(utils.get_db)):
    return crud.create_normal_user(db, user)

@router.post("/auth/login", response_model=schemas.TokenWithUserType)
def login(form_data: schemas.LoginRequest, db: Session = Depends(utils.get_db)):
    doctor = crud.get_doctor_by_email(db, form_data.email)
    if doctor and auth.verify_password(form_data.password, doctor.hashed_password):
        access_token = auth.create_access_token(data={"sub": doctor.email, "user_type": "doctor"})
        return {"doctor_id": doctor.id, "doctor_name": doctor.name , "token_type": "bearer", "user_type": "doctor", "access_token": access_token}

    normal_user = crud.get_normal_user_by_email(db, form_data.email)
    if normal_user and auth.verify_password(form_data.password, normal_user.hashed_password):
        access_token = auth.create_access_token(data={"sub": normal_user.email, "user_type": "normal_user"})
        return {"normal_user_id": normal_user.id, "normal_user_name": normal_user.name, "access_token": access_token, "token_type": "bearer", "user_type": "normal_user"}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

# Syndrome Detection Routes
@router.get("/patients/{patient_id}/detections", response_model=List[schemas.SyndromeDetectionResponse])
def get_syndrome_detections(patient_id: int, db: Session = Depends(utils.get_db)):
    detections = crud.get_syndrome_detections_by_patient(db, patient_id)
    if not detections:
        raise HTTPException(status_code=404, detail="No syndrome detections found.")
    return detections

@router.get("/users/{normal_user_id}/detections", response_model=List[schemas.SyndromeDetectionResponse])
def get_syndrome_detections_for_normal_user(normal_user_id: int, db: Session = Depends(utils.get_db)):
    detections = crud.get_syndrome_detections_by_normal_user(db, normal_user_id)
    if not detections:
        raise HTTPException(status_code=404, detail="No syndrome detections found for this user.")
    return detections

@router.post("/patients/{patient_id}/detections", response_model=schemas.SyndromeDetectionResponse)
def create_syndrome_detection_for_patient(patient_id: int, detection: schemas.SyndromeDetectionCreate, db: Session = Depends(utils.get_db)):
    return crud.create_syndrome_detection(db, detection)

@router.post("/users/{normal_user_id}/detections", response_model=schemas.SyndromeDetectionResponse)
def create_syndrome_detection_for_normal_user(normal_user_id: int, detection: schemas.SyndromeDetectionCreate, db: Session = Depends(utils.get_db)):
    return crud.create_syndrome_detection(db, detection, normal_user_id=normal_user_id)

# Patient Routes
@router.get("/patients/{doctor_id}", response_model=List[schemas.PatientResponse])
def get_patients_for_doctor(doctor_id: int, db: Session = Depends(utils.get_db)):
    patients = crud.get_patients_by_doctor_id(db, doctor_id)
    if not patients:
        raise HTTPException(status_code=404, detail="No patients found for this doctor.")
    return patients

@router.post("/patients/", response_model=schemas.PatientResponse)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(utils.get_db)):
    return crud.create_patient(db, patient)

@router.get("/patients/{patient_id}/notes", response_model=List[schemas.PatientNoteResponse])
def get_patient_notes(patient_id: int, db: Session = Depends(utils.get_db)):
    notes = crud.get_notes_by_patient(db, patient_id)
    if not notes:
        raise HTTPException(status_code=404, detail="No notes found for this patient.")
    return notes

@router.post("/patients/{patient_id}/notes", response_model=schemas.PatientNoteResponse)
def create_patient_note_for_patient(patient_id: int, note: schemas.PatientNoteCreate, db: Session = Depends(utils.get_db)):
    return crud.create_patient_note(db, note)

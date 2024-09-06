# app/routes.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import schemas, models, crud, auth, utils

router = APIRouter()

# Authentication Routes
@router.post("/auth/register", response_model=schemas.DoctorResponse)
def register_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(utils.get_db)):
    return crud.create_doctor(db, doctor)

@router.post("/auth/login", response_model=schemas.Token)
def login_doctor(form_data: auth.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(utils.get_db)):
    doctor = crud.get_doctor_by_email(db, email=form_data.username)
    if not doctor or not auth.verify_password(form_data.password, doctor.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": doctor.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Doctor Routes
@router.get("/doctors/me", response_model=schemas.DoctorResponse)
def read_current_doctor(current_doctor: models.Doctor = Depends(auth.get_current_doctor)):
    return current_doctor

@router.get("/doctors/{doctor_id}/patients", response_model=List[schemas.PatientResponse])
def read_patients(doctor_id: int, db: Session = Depends(utils.get_db), current_doctor: models.Doctor = Depends(auth.get_current_doctor)):
    utils.verify_doctor_ownership(current_doctor, doctor_id)
    patients = crud.get_patients_by_doctor(db, doctor_id)
    return patients

# Patient Routes
@router.post("/patients/", response_model=schemas.PatientResponse)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(utils.get_db), current_doctor: models.Doctor = Depends(auth.get_current_doctor)):
    utils.verify_doctor_ownership(current_doctor, patient.doctor_id)
    return crud.create_patient(db, patient)

@router.get("/patients/{patient_id}", response_model=schemas.PatientResponse)
def read_patient(patient_id: int, db: Session = Depends(utils.get_db), current_doctor: models.Doctor = Depends(auth.get_current_doctor)):
    patient = crud.get_patient_by_id(db, patient_id)
    if not patient or patient.doctor_id != current_doctor.id:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Case Routes
@router.post("/cases/", response_model=schemas.CaseResponse)
def create_case(case: schemas.CaseCreate, db: Session = Depends(utils.get_db), current_doctor: models.Doctor = Depends(auth.get_current_doctor)):
    patient = crud.get_patient_by_id(db, case.patient_id)
    if not patient or patient.doctor_id != current_doctor.id:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.create_case(db, case)

@router.get("/patients/{patient_id}/cases", response_model=List[schemas.CaseResponse])
def read_cases(patient_id: int, db: Session = Depends(utils.get_db), current_doctor: models.Doctor = Depends(auth.get_current_doctor)):
    patient = crud.get_patient_by_id(db, patient_id)
    if not patient or patient.doctor_id != current_doctor.id:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.get_cases_by_patient(db, patient_id)

# SyndromeDetection Routes
@router.post("/syndrome_detections/", response_model=schemas.SyndromeDetectionResponse)
def create_syndrome_detection(detection: schemas.SyndromeDetectionCreate, db: Session = Depends(utils.get_db), current_doctor: models.Doctor = Depends(auth.get_current_doctor)):
    patient = crud.get_patient_by_id(db, detection.patient_id)
    if not patient or patient.doctor_id != current_doctor.id:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.create_syndrome_detection(db, detection)

@router.get("/patients/{patient_id}/syndrome_detections", response_model=List[schemas.SyndromeDetectionResponse])
def read_syndrome_detections(patient_id: int, db: Session = Depends(utils.get_db), current_doctor: models.Doctor = Depends(auth.get_current_doctor)):
    patient = crud.get_patient_by_id(db, patient_id)
    if not patient or patient.doctor_id != current_doctor.id:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.get_syndrome_detections_by_patient(db, patient_id)

# PatientNote Routes
@router.post("/patient_notes/", response_model=schemas.PatientNoteResponse)
def create_patient_note(note: schemas.PatientNoteCreate, db: Session = Depends(utils.get_db), current_doctor: models.Doctor = Depends(auth.get_current_doctor)):
    patient = crud.get_patient_by_id(db, note.patient_id)
    if not patient or patient.doctor_id != current_doctor.id:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.create_patient_note(db, note)

@router.get("/patients/{patient_id}/notes", response_model=List[schemas.PatientNoteResponse])
def read_patient_notes(patient_id: int, db: Session = Depends(utils.get_db), current_doctor: models.Doctor = Depends(auth.get_current_doctor)):
    patient = crud.get_patient_by_id(db, patient_id)
    if not patient or patient.doctor_id != current_doctor.id:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.get_notes_by_patient(db, patient_id)

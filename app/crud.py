from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from . import models, schemas, auth

# Doctor CRUD Operations
def get_doctor_by_email(db: Session, email: str):
    return db.query(models.Doctor).filter(models.Doctor.email == email).first()

def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    hashed_password = auth.get_password_hash(doctor.password)
    db_doctor = models.Doctor(
        name=doctor.name,
        email=doctor.email,
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

# NormalUser CRUD Operations
def get_normal_user_by_email(db: Session, email: str):
    return db.query(models.NormalUser).filter(models.NormalUser.email == email).first()

def create_normal_user(db: Session, user: schemas.NormalUserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.NormalUser(
        name=user.name,
        email=user.email,
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

# Patient CRUD Operations
def get_patient_by_id(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(
        name=patient.name,
        doctor_id=patient.doctor_id
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

# Case CRUD Operations
def get_case_by_id(db: Session, case_id: int):
    return db.query(models.Case).filter(models.Case.id == case_id).first()

def create_case(db: Session, case: schemas.CaseCreate):
    db_case = models.Case(
        description=case.description,
        patient_id=case.patient_id
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

# SyndromeDetection CRUD Operations
def get_syndrome_detection_by_id(db: Session, detection_id: int):
    return db.query(models.SyndromeDetection).filter(models.SyndromeDetection.id == detection_id).first()

def create_syndrome_detection(db: Session, detection: schemas.SyndromeDetectionCreate):
    db_detection = models.SyndromeDetection(
        syndrome_name=detection.syndrome_name,
        patient_id=detection.patient_id
    )
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection

# PatientNote CRUD Operations
def get_patient_note_by_id(db: Session, note_id: int):
    return db.query(models.PatientNote).filter(models.PatientNote.id == note_id).first()

def create_patient_note(db: Session, note: schemas.PatientNoteCreate):
    db_note = models.PatientNote(
        note=note.note,
        patient_id=note.patient_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

# Retrieval Functions
def get_patients_by_doctor(db: Session, doctor_id: int):
    return db.query(models.Patient).filter(models.Patient.doctor_id == doctor_id).all()

def get_cases_by_patient(db: Session, patient_id: int):
    return db.query(models.Case).filter(models.Case.patient_id == patient_id).all()

def get_syndrome_detections_by_patient(db: Session, patient_id: int):
    return db.query(models.SyndromeDetection).filter(models.SyndromeDetection.patient_id == patient_id).all()

def get_notes_by_patient(db: Session, patient_id: int):
    return db.query(models.PatientNote).filter(models.PatientNote.patient_id == patient_id).all()

# app/crud.py


from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash

# Admin CRUD
def create_admin(db: Session, admin: schemas.AdminCreate):
    hashed_password = get_password_hash(admin.password)
    db_admin = models.Admin(
        name=admin.name, email=admin.email, hashed_password=hashed_password
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

# User CRUD
def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    hashed_password = get_password_hash(doctor.password)
    db_doctor = models.Doctor(
        name=doctor.name, email=doctor.email, hashed_password=hashed_password
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def create_normal_user(db: Session, user: schemas.NormalUserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.NormalUser(
        name=user.name, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Case and Detection CRUD
def create_case(db: Session, case: schemas.CaseCreate):
    db_case = models.Case(**case.dict())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

def create_detection(db: Session, detection: schemas.SyndromeDetectionCreate):
    db_detection = models.SyndromeDetection(**detection.dict())
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection

# Articles CRUD
def create_article(db: Session, article: schemas.ArticleCreate):
    db_article = models.Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_articles(db: Session):
    return db.query(models.Article).all()

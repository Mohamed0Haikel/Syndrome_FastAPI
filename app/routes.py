# app/routes.py

from typing import List, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from . import schemas, models, crud, auth, utils
from app.schemas import GenericResponse

router = APIRouter()

# Dependency
db_dependency = Depends(utils.get_db)

# # Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# --------------------------------------
# Authentication Endpoints
# --------------------------------------

@router.post("/auth/login", response_model=schemas.Token)
def login(login_request: schemas.LoginRequest, db: Session = db_dependency):
    user = auth.authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    if isinstance(user, models.Admin):
        user_type = "admin"
        user_id = user.id
    elif isinstance(user, models.Doctor):
        user_type = "doctor"
        user_id = user.id
    elif isinstance(user, models.NormalUser):
        user_type = "normal_user"
        user_id = user.id
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user type.")

    access_token = auth.create_access_token(data={"sub": user.email, "user_type": user_type, "user_id": user_id})
    return {"access_token": access_token, "token_type": "bearer", "user_type": user_type, "user_id": user_id}


# --------------------------------------
# Admin Endpoints
# --------------------------------------

@router.post("/admin/register", response_model=schemas.AdminResponse)
def register_admin(admin: schemas.AdminCreate, db: Session = db_dependency):
    return crud.create_admin(db, admin)


@router.get("/admin/articles", response_model=List[schemas.ArticleResponse])
def get_all_articles(db: Session = db_dependency):
    return crud.get_articles(db)


# @router.post("/admin/articles", response_model=schemas.ArticleResponse)
# def create_article(article: schemas.ArticleCreate, db: Session = db_dependency):
#     return crud.create_article(db, article)
@router.post("/admin/articles")
def post_article(
    title: str = Form(...),
    author: str = Form(...),
    content: str = Form(...),
    photo: UploadFile = Form(...),
    db: Session = Depends(utils.get_db)
):
    article = schemas.ArticleCreate(title=title, author=author, content=content)
    return crud.create_article(db, article, photo)

# @router.delete("/admin/users/{user_id}", status_code=204)
# def delete_user(user_id: int, db: Session = db_dependency):
#     crud.delete_user(db, user_id)
#     return {"detail": "User deleted successfully."}

@router.delete("/admin/delete/{id}/{user_type}", response_model=schemas.GenericResponse)
def delete_user_or_doctor(id: int, user_type: str, db: Session = Depends(utils.get_db)):
    """
    Delete a user or doctor based on the provided id and user_type.
    `user_type` should be either 'user' or 'doctor'.
    """
    if user_type.lower() == "user":
        user = crud.get_normal_user_by_id(db, id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {id} not found."
            )
        crud.delete_normal_user(db, id)
        return {"message": f"User with id {id} has been deleted successfully."}
    
    elif user_type.lower() == "doctor":
        doctor = crud.get_doctor_by_id(db, id)
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor with id {id} not found."
            )
        crud.delete_doctor(db, id)
        return {"message": f"Doctor with id {id} has been deleted successfully."}
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_type. It must be either 'user' or 'doctor'."
        )


# @router.get("/admin/users", response_model=List[schemas.NormalUserResponse])
# def view_all_normal_users(db: Session = Depends(utils.get_db), current_admin: schemas.AdminResponse = Depends(auth.get_current_user)):
#     if not isinstance(current_admin, schemas.AdminResponse):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to view users.",
#         )
#     return crud.get_all_normal_users(db)
@router.get("/admin/users", response_model=List[schemas.NormalUserResponse])
def view_all_normal_users(db: Session = Depends(utils.get_db)):
    """Fetch a list of all normal users."""
    return crud.get_all_normal_users(db)


# @router.get("/admin/doctors", response_model=List[schemas.DoctorResponse])
# def view_all_doctors(db: Session = Depends(utils.get_db), current_admin: schemas.AdminResponse = Depends(auth.get_current_user)):
#     if not isinstance(current_admin, schemas.AdminResponse):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to view doctors.",
#         )
#     return crud.get_all_doctors(db)
@router.get("/admin/doctors", response_model=List[schemas.DoctorResponse])
def view_all_doctors(db: Session = Depends(utils.get_db)):
    """Fetch a list of all doctors."""
    return crud.get_all_doctors(db)

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
    cases = crud.get_cases_by_doctor(db, doctor_id)
    if not cases:
        raise HTTPException(status_code=404, detail="No cases found for this doctor.")
    return cases


@router.post("/doctor/detections", response_model=schemas.SyndromeDetectionResponse)
def create_detection_for_case(detection: schemas.SyndromeDetectionCreate, db: Session = db_dependency):
    if not detection.case_id:
        raise HTTPException(status_code=400, detail="Case ID is required for doctor detections.")
    return crud.create_detection(db, detection)


@router.get("/doctor/detections/{case_id}", response_model=List[schemas.SyndromeDetectionResponse])
def get_detections_for_case(case_id: int, db: Session = db_dependency):
    detections = crud.get_detections_by_case(db, case_id)
    if not detections:
        raise HTTPException(status_code=404, detail="No detections found for this case.")
    return detections


@router.get("/doctor/detection-history/{doctor_id}", response_model=List[schemas.SyndromeDetectionResponse])
def get_detection_history_for_doctor(doctor_id: int, db: Session = db_dependency):
    # Assuming detection history for a doctor is all detections across their cases
    cases = crud.get_cases_by_doctor(db, doctor_id)
    detections = []
    for case in cases:
        detections.extend(crud.get_detections_by_case(db, case.id))
    if not detections:
        raise HTTPException(status_code=404, detail="No detection history found for this doctor.")
    return detections


# --------------------------------------
# Normal User Endpoints
# --------------------------------------

@router.post("/user/register", response_model=schemas.NormalUserResponse)
def register_normal_user(user: schemas.NormalUserCreate, db: Session = db_dependency):
    return crud.create_normal_user(db, user)


@router.post("/user/detections", response_model=schemas.SyndromeDetectionResponse)
def create_detection_for_user(detection: schemas.SyndromeDetectionCreate, db: Session = db_dependency):
    if not detection.normal_user_id:
        raise HTTPException(status_code=400, detail="User ID is required for user detections.")
    return crud.create_detection(db, detection)


@router.get("/user/detections/{user_id}", response_model=List[schemas.SyndromeDetectionResponse])
def get_detections_for_user(user_id: int, db: Session = db_dependency):
    detections = crud.get_detections_by_user(db, user_id)
    if not detections:
        raise HTTPException(status_code=404, detail="No detections found for this user.")
    return detections


@router.get("/user/profile/{user_id}", response_model=schemas.NormalUserResponse)
def get_user_profile(user_id: int, db: Session = db_dependency):
    user = crud.get_normal_user_by_email(db, email=None)  # You might need a separate function to get by ID
    user = db.query(models.NormalUser).filter(models.NormalUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


# --------------------------------------
# Additional Admin Functionality (Optional)
# --------------------------------------

@router.get("/admin/users", response_model=List[schemas.DoctorResponse])
def get_all_users(db: Session = db_dependency):
    doctors = crud.get_all_doctors(db)
    normal_users = crud.get_all_normal_users(db)
    admins = crud.get_all_admins(db)
    return {"admins": admins, "doctors": doctors, "normal_users": normal_users}

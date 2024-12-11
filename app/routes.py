# app/routes.py

from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
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
        access_token = auth.create_access_token(data={"sub": user.email, "user_type": user_type, "user_id": user_id})
        return {"access_token": access_token, "token_type": "bearer", "user_type": user_type, "user_id": user_id}
    
    elif isinstance(user, models.Doctor):
        user_type = "doctor"
        user_id = user.id
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "profile_image": user.profile_image,
        }

    elif isinstance(user, models.NormalUser):
        user_type = "normal_user"
        user_id = user.id
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "profile_image": user.profile_image,
        }

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user type.")

    access_token = auth.create_access_token(data={"sub": user.email, "user_type": user_type, "user_id": user_id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": user_type,
        "user_id": user_id,
        "user_data": user_data,
    }


# --------------------------------------
# Admin Endpoints
# --------------------------------------

@router.post("/admin/register", response_model=schemas.AdminResponse)
def register_admin(admin: schemas.AdminCreate, db: Session = db_dependency):
    return crud.create_admin(db, admin)


@router.get("/admin/articles", response_model=List[schemas.ArticleResponse])
def get_all_articles(db: Session = db_dependency):
    return crud.get_articles(db)



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

@router.delete("/admin/articles/{article_id}", response_model=schemas.GenericResponse)
def delete_article(article_id: int, db: Session = Depends(utils.get_db)):
    """
    Endpoint to delete an article by its ID.
    """
    success = crud.delete_article(db, article_id)
    if success:
        return {"success": True, "message": "Article deleted successfully."}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete the article.")


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


@router.get("/admin/users", response_model=List[schemas.NormalUserResponse])
def view_all_normal_users(db: Session = Depends(utils.get_db)):
    """Fetch a list of all normal users."""
    return crud.get_all_normal_users(db)



@router.get("/admin/doctors", response_model=List[schemas.DoctorResponse])
def view_all_doctors(db: Session = Depends(utils.get_db)):
    """Fetch a list of all doctors."""
    return crud.get_all_doctors(db)

# --------------------------------------
# Doctor Endpoints
# --------------------------------------



@router.post("/doctor/register", response_model=schemas.DoctorResponse)
def register_doctor(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_image: UploadFile = File(...),
    db: Session = db_dependency
):
    doctor = schemas.DoctorCreate(
        name=name,
        phone=phone,
        email=email,
        password=password
    )
    return crud.create_doctor(db, doctor, profile_image)

# POST: Add a case for a specific doctor
@router.post("/doctor/cases/{doctor_id}", response_model=schemas.CaseResponse)
def create_case(
    doctor_id: int,
    # title: str = Form(...),
    description: str = Form(...),
    db: Session = db_dependency
):
    # Validate the doctor exists
    doctor = crud.get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")

    # Create a new case
    case_data = schemas.CaseCreate(
        doctor_id=doctor_id,
        # title=title,
        description=description
    )
    return crud.create_case(db, case_data)



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
def register_normal_user(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_image: UploadFile = File(...),
    db: Session = db_dependency
):
    # Create a NormalUserCreate object
    user = schemas.NormalUserCreate(
        name=name,
        phone=phone,
        email=email,
        password=password
    )
    return crud.create_normal_user(db, user, profile_image)

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





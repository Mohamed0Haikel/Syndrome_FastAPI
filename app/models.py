# app/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)

    cases = relationship("Case", back_populates="doctor", cascade="all, delete")

class NormalUser(Base):
    __tablename__ = "normal_users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    # profile_data = Column(Text, nullable=True)

    syndrome_detections = relationship("SyndromeDetection", back_populates="normal_user", cascade="all, delete")

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)

    doctor = relationship("Doctor", back_populates="cases")
    syndrome_detections = relationship("SyndromeDetection", back_populates="case", cascade="all, delete")

class SyndromeDetection(Base):
    __tablename__ = "syndrome_detections"
    id = Column(Integer, primary_key=True, index=True)
    result = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    normal_user_id = Column(Integer, ForeignKey("normal_users.id"), nullable=True)

    case = relationship("Case", back_populates="syndrome_detections")
    normal_user = relationship("NormalUser", back_populates="syndrome_detections")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    photo_url = Column(String, nullable=False)
    content = Column(Text, nullable=False)

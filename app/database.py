# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if not os.path.exists(dotenv_path):
    logger.warning(".env file not found. Ensure DATABASE_URL is set as an environment variable.")
else:
    load_dotenv(dotenv_path=dotenv_path)

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables. Check your .env file or environment setup.")

logger.info(f"Using database: {DATABASE_URL}")

# Create database engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """
    Initialize the database by creating all tables.
    Import all models here to ensure they are registered with SQLAlchemy.
    """
    from .models import Admin, Doctor, NormalUser, Case, SyndromeDetection, Article
    
    logger.info("Initializing the database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully.")

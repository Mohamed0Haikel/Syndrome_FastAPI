# app/__init__.py

from fastapi import FastAPI 

from .database import engine, Base, init_db
from .routes import router
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def create_app():
    app = FastAPI(title="Syndrome API", version="1.0.0")

    # Initialize database
    init_db()

    # Include API routers
    app.include_router(router)

    return app

app = create_app()

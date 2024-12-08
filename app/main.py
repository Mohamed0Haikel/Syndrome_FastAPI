# app/main.py


# from fastapi import FastAPI
# from .routes import router
# from .database import init_db
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import router

app = FastAPI(title="Syndrome API", version="0.112.2")


# Serve the "media" directory for uploaded files
media_path = os.path.join(os.getcwd(), "media")
app.mount("/media", StaticFiles(directory=media_path), name="media")

# Include your routers or other configurations
app.include_router(router)



@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI project!"}

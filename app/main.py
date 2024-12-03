# app/main.py


# from fastapi import FastAPI
# from .routes import router
# from .database import init_db
from fastapi import FastAPI
from .routes import router

app = FastAPI(title="Syndrome API", version="0.112.2")

# Include your routers or other configurations
app.include_router(router)


# app = FastAPI()

# app.include_router(router)

# @app.on_event("startup")
# def on_startup():
#     init_db()  # Initialize the database when the app starts

@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI project!"}

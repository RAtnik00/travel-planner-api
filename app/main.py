from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routers import projects

Base.metadata.create_all(engine)

app = FastAPI(title="Travel Planner API")
app.include_router(projects.router)


@app.get("/")
def read_root():
    return {"message": "Travel Planner API is running"}
from fastapi import FastAPI

from app.database import Base, engine
from app import models

Base.metadata.create_all(engine)

app = FastAPI(title="Travel Planner API")


@app.get("/")
def read_root():
    return {"message": "Travel Planner API is running"}
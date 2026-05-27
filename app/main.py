from fastapi import Depends, FastAPI

from app.database import Base, engine
from app import models
from app.routers import places, projects
from app.auth import require_basic_auth

Base.metadata.create_all(engine)

app = FastAPI(title="Travel Planner API")
app.include_router(projects.router, dependencies=[Depends(require_basic_auth)])
app.include_router(places.router, dependencies=[Depends(require_basic_auth)])


@app.get("/")
def read_root():
    return {"message": "Travel Planner API is running"}

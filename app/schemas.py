from datetime import date

from pydantic import BaseModel, Field


class PlaceInput(BaseModel):
    external_id: str = Field(..., min_length=1)
    notes: str | None = None


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    start_date: date | None = None


class ProjectCreate(ProjectBase):
    places: list[PlaceInput] = Field(default_factory=list, max_length=10)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    start_date: date | None = None


class PlaceUpdate(BaseModel):
    notes: str | None = None
    visited: bool | None = None


class PlaceResponse(BaseModel):
    id: int
    project_id: int
    external_id: str
    title: str
    notes: str | None
    visited: bool

    model_config = {"from_attributes": True}


class ProjectResponse(ProjectBase):
    id: int
    completed: bool
    places: list[PlaceResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}

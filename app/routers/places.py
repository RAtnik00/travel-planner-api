from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.artic import get_artwork_by_id

router = APIRouter(
    prefix="/projects/{project_id}/places",
    tags=["places"],
)


def get_project_or_404(project_id: int, db: Session) -> models.TravelProject:
    project = db.get(models.TravelProject, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


def update_project_completion(project: models.TravelProject) -> None:
    if project.places:
        project.completed = all(place.visited for place in project.places)
    else:
        project.completed = False


@router.post(
    "",
    response_model=schemas.PlaceResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_place_to_project(
    project_id: int,
    place_data: schemas.PlaceInput,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)

    if len(project.places) >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A project cannot contain more than 10 places",
        )

    duplicate_place = (
        db.query(models.ProjectPlace)
        .filter(
            models.ProjectPlace.project_id == project_id,
            models.ProjectPlace.external_id == place_data.external_id,
        )
        .first()
    )

    if duplicate_place is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This external place is already added to the project",
        )

    artwork = get_artwork_by_id(place_data.external_id)

    place = models.ProjectPlace(
        project_id=project.id,
        external_id=artwork["external_id"],
        title=artwork["title"],
        notes=place_data.notes,
    )

    db.add(place)
    update_project_completion(project)
    db.commit()
    db.refresh(place)

    return place


@router.get("", response_model=list[schemas.PlaceResponse])
def list_project_places(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)

    return (
        db.query(models.ProjectPlace)
        .filter(models.ProjectPlace.project_id == project_id)
        .all()
    )


@router.get("/{place_id}", response_model=schemas.PlaceResponse)
def get_project_place(
    project_id: int,
    place_id: int,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)

    place = (
        db.query(models.ProjectPlace)
        .filter(
            models.ProjectPlace.id == place_id,
            models.ProjectPlace.project_id == project_id,
        )
        .first()
    )

    if place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found",
        )

    return place


@router.patch("/{place_id}", response_model=schemas.PlaceResponse)
def update_project_place(
    project_id: int,
    place_id: int,
    place_data: schemas.PlaceUpdate,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)

    place = (
        db.query(models.ProjectPlace)
        .filter(
            models.ProjectPlace.id == place_id,
            models.ProjectPlace.project_id == project_id,
        )
        .first()
    )

    if place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found",
        )

    update_data = place_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(place, field, value)

    update_project_completion(project)

    db.commit()
    db.refresh(place)

    return place
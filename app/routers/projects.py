from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.artic import get_artwork_by_id

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=schemas.ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project_data: schemas.ProjectCreate,
    db: Session = Depends(get_db),
):
    project = models.TravelProject(
        name=project_data.name,
        description=project_data.description,
        start_date=project_data.start_date,
    )

    seen_external_ids = set()

    for place_data in project_data.places:
        artwork = get_artwork_by_id(place_data.external_id)

        if artwork["external_id"] in seen_external_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate external place in project creation request",
            )

        seen_external_ids.add(artwork["external_id"])

        project.places.append(
            models.ProjectPlace(
                external_id=artwork["external_id"],
                title=artwork["title"],
                notes=place_data.notes,
            )
        )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.get("", response_model=list[schemas.ProjectResponse])
def list_projects(
    completed: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.TravelProject)

    if completed is not None:
        query = query.filter(models.TravelProject.completed == completed)

    return query.offset(skip).limit(limit).all()


@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.TravelProject, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.patch("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(
    project_id: int,
    project_data: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = db.get(models.TravelProject, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    update_data = project_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.TravelProject, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    has_visited_places = any(place.visited for place in project.places)

    if has_visited_places:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a project with visited places",
        )

    db.delete(project)
    db.commit()

    return None

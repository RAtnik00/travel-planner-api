from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TravelProject(Base):
    __tablename__ = "travel_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    places: Mapped[list["ProjectPlace"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectPlace(Base):
    __tablename__ = "project_places"
    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="uq_project_external_place"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("travel_projects.id"),
        nullable=False,
    )

    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    visited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    project: Mapped[TravelProject] = relationship(back_populates="places")
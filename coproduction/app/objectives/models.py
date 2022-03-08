import uuid
from datetime import datetime
from typing import TypedDict

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app.general.db.base_class import Base as BaseModel
from sqlalchemy.dialects.postgresql import HSTORE
from app.translations import translation_hybrid


class ObjectiveMetadata(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE)

    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)

    # belongs to a phasemetadata
    phasemetadata_id = Column(
        UUID(as_uuid=True), ForeignKey("phasemetadata.id", ondelete='CASCADE')
    )
    phasemetadata = relationship("PhaseMetadata", back_populates="objectivemetadatas")

    taskmetadatas = relationship("TaskMetadata", back_populates="objectivemetadata")

    def __repr__(self):
        return "<ObjectiveMetadata %r>" % self.name_translations["en"]


class Objective(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    progress = Column(Integer, default=0)
    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE)

    name = Column(String)
    description = Column(String)

    # belongs to a phase
    phase_id = Column(
        UUID(as_uuid=True), ForeignKey("phase.id", ondelete='CASCADE')
    )
    phase = relationship("Phase", back_populates="objectives")

    tasks = relationship("Task", back_populates="objective")

    @property
    def start_date(self) -> Date:
        lowest = None
        for task in self.tasks:
            if task.start_date:
                if not lowest or task.start_date < lowest:
                    lowest = task.start_date
        return lowest

    @property
    def end_date(self) -> Date:
        greatest = None
        for task in self.tasks:
            if task.end_date:
                if not greatest or task.end_date > greatest:
                    greatest = task.end_date
        return greatest

    def __repr__(self):
        return "<Objective %r>" % self.name

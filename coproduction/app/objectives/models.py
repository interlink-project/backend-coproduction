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
    func,
)
from sqlalchemy.dialects.postgresql import HSTORE, UUID
from sqlalchemy.orm import backref, reconstructor, relationship
from sqlalchemy_utils import aggregated

from app.general.db.base_class import Base as BaseModel
from app.tasks.models import Status, Task
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

    @aggregated('tasks', Column(Date))
    def end_date(self):
        return func.max(Task.end_date)

    @aggregated('tasks', Column(Date))
    def start_date(self):
        return func.min(Task.start_date)

    tasks = relationship("Task", back_populates="objective")

    @reconstructor
    def init_on_load(self):
        statuses = [task.status for task in self.tasks]

        if all([x == Status.finished for x in statuses]):
            self.status = Status.finished
        elif all([x == Status.awaiting for x in statuses]):
            self.status = Status.awaiting
        else:
            self.status = Status.in_progress

        countInProgress = statuses.count(Status.in_progress) / 2
        countFinished = statuses.count(Status.finished)
        self.progress = int((countInProgress + countFinished) * 100 / len(statuses))

    def __repr__(self):
        return "<task %r>" % self.name

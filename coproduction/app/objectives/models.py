from email.policy import default
import uuid
from datetime import datetime
from typing import TypedDict

from sqlalchemy import (
    Enum,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    Numeric,
    func,
)
from sqlalchemy.dialects.postgresql import HSTORE, UUID
from sqlalchemy.orm import backref, reconstructor, relationship
from sqlalchemy_utils import aggregated

from app.general.db.base_class import Base as BaseModel
from app.tasks.models import Status, Task
from app.translations import translation_hybrid


prerequisites_metadata = Table(
    'objective_metadata_prerequisites', BaseModel.metadata,
    Column('objectivemetadata_a_id', ForeignKey('objectivemetadata.id'), primary_key=True),
    Column('objectivemetadata_b_id', ForeignKey('objectivemetadata.id'), primary_key=True)
)

prerequisites = Table(
    'objective_prerequisites', BaseModel.metadata,
    Column('objective_a_id', ForeignKey('objective.id'), primary_key=True),
    Column('objective_b_id', ForeignKey('objective.id'), primary_key=True)
)

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

    # prerequisites
    prerequisites = relationship("ObjectiveMetadata", secondary=prerequisites_metadata,
                                 primaryjoin=id == prerequisites_metadata.c.objectivemetadata_a_id,
                                 secondaryjoin=id == prerequisites_metadata.c.objectivemetadata_b_id,
                                 )
                                 
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

    # prerequisites
    prerequisites = relationship("Objective", secondary=prerequisites,
                                 primaryjoin=id == prerequisites.c.objective_a_id,
                                 secondaryjoin=id == prerequisites.c.objective_b_id,
                                 )

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
    status = Column(Enum(Status, create_constraint=False, native_enum=False), default=Status.awaiting)
    progress = Column(Numeric, default=0)

    def __repr__(self):
        return "<task %r>" % self.name
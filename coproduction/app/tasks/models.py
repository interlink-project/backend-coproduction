import uuid
from typing import TypedDict
import enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Enum,
    Table,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import backref, relationship

from app.general.db.base_class import Base as BaseModel
from sqlalchemy.dialects.postgresql import HSTORE
from app.translations import translation_hybrid

prerequisites_metadata = Table(
    'tasks_metadata_prerequisites', BaseModel.metadata,
    Column('taskmetadata_a_id', ForeignKey('taskmetadata.id'), primary_key=True),
    Column('taskmetadata_b_id', ForeignKey('taskmetadata.id'), primary_key=True)
)

prerequisites = Table(
    'task_prerequisites', BaseModel.metadata,
    Column('task_a_id', ForeignKey('task.id'), primary_key=True),
    Column('task_b_id', ForeignKey('task.id'), primary_key=True)
)

class TaskMetadata(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE)

    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)

    # belongs to an objetive
    objectivemetadata_id = Column(
        UUID(as_uuid=True), ForeignKey("objectivemetadata.id", ondelete='CASCADE')
    )
    objectivemetadata = relationship("ObjectiveMetadata", back_populates="taskmetadatas")

    problem_profiles = Column(ARRAY(String), default=list)
    
    # prerequisites
    prerequisites = relationship("TaskMetadata", secondary=prerequisites_metadata,
                                 primaryjoin=id == prerequisites_metadata.c.taskmetadata_a_id,
                                 secondaryjoin=id == prerequisites_metadata.c.taskmetadata_b_id,
    )

    def __repr__(self):
        return "<TaskMetadata %r>" % self.name_translations["en"]


class Status(enum.Enum):
    awaiting = "awaiting"
    in_progress = "in_progress"
    finished = "finished"

class Task(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)

    # belongs to an objetive
    objective_id = Column(
        UUID(as_uuid=True), ForeignKey("objective.id", ondelete='CASCADE')
    )
    objective = relationship("Objective", back_populates="tasks")

    # prerequisites
    prerequisites = relationship("Task", secondary=prerequisites,
                                 primaryjoin=id == prerequisites.c.task_a_id,
                                 secondaryjoin=id == prerequisites.c.task_b_id,
                                 )

    """
    # save from where has been forked
    parent_id = Column(UUID(as_uuid=True), ForeignKey("task.id"))
    children = relationship(
        "Task", backref=backref("parent", remote_side=[id])
    )
    """

    problem_profiles = Column(ARRAY(String), default=list)
    assets = relationship("Asset", back_populates="task")

    status = Column(Enum(Status, create_constraint=False, native_enum=False), default=Status.awaiting)
    
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    def __repr__(self):
        return "<Task %r>" % self.name

from typing import TypedDict

from app.general.db.base_class import Base as BaseModel
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid

class Task(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_public = Column(Boolean)
    name = Column(String)
    description = Column(String)
    objective_id = Column(
        UUID(as_uuid=True), ForeignKey("objective.id", ondelete='CASCADE')
    )
    objective = relationship("Objective", back_populates="tasks")

    instantiations = relationship("TaskInstantiation", back_populates="task")
    
    def __repr__(self):
        return "<Task %r>" % self.name

class TaskInstantiation(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assets = relationship("Asset", back_populates="taskinstantiation")

    objectiveinstantiation_id = Column(
        UUID(as_uuid=True), ForeignKey("objectiveinstantiation.id", ondelete='CASCADE')
    )
    objectiveinstantiation = relationship("ObjectiveInstantiation", back_populates="taskinstantiations")
    
    task_id = Column(
        UUID(as_uuid=True), ForeignKey("task.id", ondelete='CASCADE')
    )
    task = relationship("Task", back_populates="instantiations")
    
    @property
    def name(self) -> str:
        return self.task.name

    @property
    def description(self) -> str:
        return self.task.description

    def __repr__(self):
        return "<TaskInstatiation %r>" % self.task.name
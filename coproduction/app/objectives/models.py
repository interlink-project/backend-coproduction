from datetime import datetime
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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class Objective(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_public = Column(Boolean)
    name = Column(String)
    description = Column(String)
    phase_id = Column(
        UUID(as_uuid=True), ForeignKey("phase.id", ondelete='CASCADE')
    )
    phase = relationship("Phase", back_populates="objectives")
    tasks = relationship("Task", back_populates="objective")

    instantiations = relationship("ObjectiveInstantiation", back_populates="objective")

    def __repr__(self):
        return "<Objective %r>" % self.name

class ObjectiveInstantiation(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    phaseinstantiation_id = Column(
        UUID(as_uuid=True), ForeignKey("phaseinstantiation.id", ondelete='CASCADE')
    )
    phaseinstantiation = relationship("PhaseInstantiation", back_populates="objectiveinstantiations")

    objective_id = Column(
        UUID(as_uuid=True), ForeignKey("objective.id", ondelete='CASCADE')
    )
    objective = relationship("Objective", back_populates="instantiations")
    taskinstantiations = relationship("TaskInstantiation", back_populates="objectiveinstantiation")
    
    progress = Column(Integer, default=0)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)


    def __repr__(self):
        return "<ObjectiveInstatiation %r>" % self.objective.name
    
    @property
    def name(self):
        return self.objective.name

    @property
    def description(self):
        return self.objective.description

    @property
    def tasks_length(self):
        if not self.taskinstantiations:
            return 0
        
        return len(self.taskinstantiations)
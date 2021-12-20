from datetime import datetime, timedelta
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
from app.tables import coproductionschema_phase_association_table
import uuid

class Phase(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_public = Column(Boolean)
    name = Column(String)
    description = Column(String)
    instantiations = relationship("PhaseInstantiation", back_populates="phase")
    objectives = relationship("Objective", back_populates="phase")

    schemas = relationship(
        "CoproductionSchema",
        secondary=coproductionschema_phase_association_table,
        back_populates="phases",
    )
    def __repr__(self):
        return "<Phase %r>" % self.name

class PhaseInstantiation(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = relationship("CoproductionProcess", back_populates="phaseinstantiations")

    phase_id = Column(
        UUID(as_uuid=True), ForeignKey("phase.id", ondelete='CASCADE')
    )
    phase = relationship("Phase", back_populates="instantiations")

    objectiveinstantiations = relationship("ObjectiveInstantiation", back_populates="phaseinstantiation")

    @property
    def name(self) -> str:
        return self.phase.name

    @property
    def description(self) -> str:
        return self.phase.description

    def __repr__(self):
        return "<PhaseInstatiation %r>" % self.phase.name

    @property
    def progress(self):
        fin = 0
        tot = 0
        for objective in self.objectiveinstantiations:
            fin += objective.progress
            tot += 1
        return int(fin / tot)

    @property
    def start_date(self):
        lowest = None
        for objective in self.objectiveinstantiations:
            if objective.start_date:
                var = datetime.strptime(objective.start_date, "%Y-%m-%d")
                if not lowest or var < lowest:
                    lowest = var
        return lowest
    
    @property
    def end_date(self):
        greatest = None
        for objective in self.objectiveinstantiations:
            if objective.end_date:
                var = datetime.strptime(objective.end_date, "%Y-%m-%d")
                if not greatest or var > greatest:
                    greatest = var
        return greatest
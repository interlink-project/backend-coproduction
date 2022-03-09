from cmath import pi
import uuid
from datetime import datetime, timedelta
from typing import TypedDict

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    Date
)
from sqlalchemy.dialects.postgresql import HSTORE, UUID
from sqlalchemy.orm import backref, relationship, reconstructor
from app.general.db.base_class import Base as BaseModel
from app.translations import translation_hybrid
from app.tasks.models import Status

prerequisites_metadata = Table(
    'metadata_prerequisites', BaseModel.metadata,
    Column('phasemetadata_a_id', ForeignKey('phasemetadata.id'), primary_key=True),
    Column('phasemetadata_b_id', ForeignKey('phasemetadata.id'), primary_key=True)
)

prerequisites = Table(
    'prerequisites', BaseModel.metadata,
    Column('phase_a_id', ForeignKey('phase.id'), primary_key=True),
    Column('phase_b_id', ForeignKey('phase.id'), primary_key=True)
)


class PhaseMetadata(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE)

    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)

    # prerequisites
    prerequisites = relationship("PhaseMetadata", secondary=prerequisites_metadata,
                                 primaryjoin=id == prerequisites_metadata.c.phasemetadata_a_id,
                                 secondaryjoin=id == prerequisites_metadata.c.phasemetadata_b_id,
                                 )

    # or can belong to an schema
    coproductionschema_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionschema.id", ondelete='CASCADE')
    )
    coproductionschema = relationship(
        "CoproductionSchema", back_populates="phasemetadatas")

    objectivemetadatas = relationship(
        "ObjectiveMetadata", back_populates="phasemetadata")

    @property
    def prerequisites_ids(self):
        return [pr.id for pr in self.prerequisites]
        
    def __repr__(self):
        return "<PhaseMetadata %r>" % self.name_translations["en"]


class Phase(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)

    # prerequisites
    prerequisites = relationship("Phase", secondary=prerequisites,
                                 primaryjoin=id == prerequisites.c.phase_a_id,
                                 secondaryjoin=id == prerequisites.c.phase_b_id,
                                 )

    # they belong to a process
    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = relationship("CoproductionProcess", back_populates="phases")

    objectives = relationship("Objective", back_populates="phase")

    def __repr__(self):
        return "<Phase %r>" % self.name

    @property
    def prerequisites_ids(self):
        return [pr.id for pr in self.prerequisites]
    
   
    @reconstructor
    def init_on_load(self):
        # SETS start_date, end_date and status based on its objectives
        lowest = None
        greatest = None
        statuses = []
        
        for objective in self.objectives:
            if objective.start_date and (not lowest or objective.start_date < lowest):
                lowest = objective.start_date
            if objective.end_date and (not greatest or objective.end_date > greatest):
                greatest = objective.end_date
            statuses.append(objective.status)

        if all([x == Status.finished for x in statuses]):
            self.status = Status.finished
        elif all([x == Status.awaiting for x in statuses]):
            self.status = Status.awaiting
        else: 
            self.status = Status.in_progress
        
        countInProgress = statuses.count(Status.in_progress) / 2
        countFinished = statuses.count(Status.finished)
        self.progress = int((countInProgress + countFinished) * 100 / len(statuses))
        self.start_date = lowest
        self.end_date = greatest
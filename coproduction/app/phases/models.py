import uuid
from cmath import pi
from datetime import datetime, timedelta
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
    'phases_metadata_prerequisites', BaseModel.metadata,
    Column('phasemetadata_a_id', ForeignKey('phasemetadata.id'), primary_key=True),
    Column('phasemetadata_b_id', ForeignKey('phasemetadata.id'), primary_key=True)
)

prerequisites = Table(
    'phase_prerequisites', BaseModel.metadata,
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

    def __repr__(self):
        return "<Phase %r>" % self.name

    @property
    def prerequisites_ids(self):
        return [pr.id for pr in self.prerequisites]

    @aggregated('objectives.tasks', Column(Date))
    def end_date(self):
        return func.max(Task.end_date)

    @aggregated('objectives.tasks', Column(Date))
    def start_date(self):
        return func.min(Task.start_date)

    objectives = relationship("Objective", back_populates="phase")
    status = Column(Enum(Status, create_constraint=False, native_enum=False), default=Status.awaiting)
    progress = Column(Numeric, default=0)
    
import uuid

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import HSTORE, UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import aggregated

from app.general.db.base_class import Base as BaseModel
from app.tasks.models import Status, Task

prerequisites = Table(
    'objective_prerequisites', BaseModel.metadata,
    Column('objective_a_id', ForeignKey('objective.id'), primary_key=True),
    Column('objective_b_id', ForeignKey('objective.id'), primary_key=True)
)


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

    @property
    def prerequisites_ids(self):
        return [pr.id for pr in self.prerequisites]

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
    status = Column(Enum(Status, create_constraint=False,
                    native_enum=False), default=Status.awaiting)
    progress = Column(Numeric, default=0)

    def __repr__(self):
        return "<task %r>" % self.name

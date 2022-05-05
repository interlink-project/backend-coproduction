import uuid
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
from sqlalchemy.orm import relationship

from app.general.db.base_class import Base as BaseModel
from sqlalchemy.ext.associationproxy import association_proxy

prerequisites = Table(
    'task_prerequisites', BaseModel.metadata,
    Column('task_a_id', ForeignKey('task.id'), primary_key=True),
    Column('task_b_id', ForeignKey('task.id', ondelete="CASCADE"), primary_key=True)
)

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

    prerequisites_ids = association_proxy('prerequisites', 'id')
        
    problemprofiles = Column(ARRAY(String), default=list)
    assets = relationship("Asset", back_populates="task", cascade="all,delete")

    status = Column(Enum(Status, create_constraint=False, native_enum=False), default=Status.awaiting)
    
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    def __repr__(self):
        return "<Task %r>" % self.name

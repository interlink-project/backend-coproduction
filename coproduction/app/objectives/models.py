import uuid
from datetime import datetime
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
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app.general.db.base_class import Base as BaseModel
from sqlalchemy.dialects.postgresql import HSTORE
from app.translations import translation_hybrid


class Objective(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_public = Column(Boolean, default=True)
    progress = Column(Integer, default=0)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)

    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE)

    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)

    # belongs to a phase
    phase_id = Column(
        UUID(as_uuid=True), ForeignKey("phase.id", ondelete='CASCADE')
    )
    phase = relationship("Phase", back_populates="objectives")

    # save from where has been forked
    parent_id = Column(UUID(as_uuid=True), ForeignKey("objective.id"))
    children = relationship(
        "Objective", backref=backref("parent", remote_side=[id])
    )

    tasks = relationship("Task", back_populates="objective")

    def __repr__(self):
        return "<Objective %r>" % self.name

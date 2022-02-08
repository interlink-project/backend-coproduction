import uuid
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
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import backref, relationship

from app.general.db.base_class import Base as BaseModel
from sqlalchemy.dialects.postgresql import HSTORE
from app.translations import translation_hybrid


class Task(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_public = Column(Boolean, default=True)
    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE)

    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)

    # belongs to an objetive
    objective_id = Column(
        UUID(as_uuid=True), ForeignKey("objective.id", ondelete='CASCADE')
    )
    objective = relationship("Objective", back_populates="tasks")

    # save from where has been forked
    parent_id = Column(UUID(as_uuid=True), ForeignKey("task.id"))
    children = relationship(
        "Task", backref=backref("parent", remote_side=[id])
    )

    problem_profiles = Column(ARRAY(String), default=list)
    assets = relationship("Asset", back_populates="task")

    def __repr__(self):
        return "<Task %r>" % self.name

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
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app.general.db.base_class import Base as BaseModel
from sqlalchemy.dialects.postgresql import HSTORE
from app.translations import translation_hybrid


class Phase(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_public = Column(Boolean, default=True)
    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE)

    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)

    # can belong to a process
    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = relationship("CoproductionProcess", back_populates="phases")

    # or can belong to an schema
    coproductionschema_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionschema.id", ondelete='CASCADE')
    )
    coproductionschema = relationship("CoproductionSchema", back_populates="phases")

    # save from where has been forked
    parent_id = Column(UUID(as_uuid=True), ForeignKey("phase.id"))
    children = relationship(
        "Phase", backref=backref("parent", remote_side=[id])
    )

    objectives = relationship("Objective", back_populates="phase")

    def __repr__(self):
        return "<Phase %r>" % self.name

    @property
    def progress(self):
        fin = 0
        tot = 0
        for objective in self.objectives:
            fin += objective.progress
            tot += 1
        try:
            return int(fin / tot)
        except:
            return 0

    @property
    def start_date(self):
        lowest = None
        for objective in self.objectives:
            if objective.start_date:
                var = datetime.strptime(objective.start_date, "%Y-%m-%d")
                if not lowest or var < lowest:
                    lowest = var
        return lowest

    @property
    def end_date(self):
        greatest = None
        for objective in self.objectives:
            if objective.end_date:
                var = datetime.strptime(objective.end_date, "%Y-%m-%d")
                if not greatest or var > greatest:
                    greatest = var
        return greatest

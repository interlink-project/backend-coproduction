import uuid

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import backref, relationship

from app.treeitems.models import TreeItem


class Task(TreeItem):
    id = Column(
        UUID(as_uuid=True),
        ForeignKey("treeitem.id", ondelete="CASCADE"),
        primary_key=True,
        default=uuid.uuid4,
    )
    problemprofiles = Column(ARRAY(String), default=dict)

    # they belong to an objetive
    objective_id = Column(
        UUID(as_uuid=True), ForeignKey("objective.id", ondelete='CASCADE')
    )
    objective = relationship("Objective", foreign_keys=[
                             objective_id], backref=backref('children', passive_deletes=True))

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "task",
    }

    def __repr__(self):
        return "<Task %r>" % self.name

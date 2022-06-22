import uuid

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    String,
    Integer,
    func
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import backref, relationship

from app.treeitems.models import TreeItem
from sqlalchemy.ext.hybrid import hybrid_property


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
    
    @property
    def coproductionprocess(self):
        return self.objective.phase.coproductionprocess

    @hybrid_property
    def phase_id(self):
        return self.objective.phase_id

    @hybrid_property
    def path_ids(self):
        return [self.objective.phase_id, self.objective_id, self.id]
    
    @hybrid_property
    def is_disabled(self):
        return (self.disabled_on is not None) or (self.objective.disabled_on is not None) or (self.objective.phase.disabled_on) is not None

    def __repr__(self):
        return "<Task %r>" % self.name

import uuid

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Numeric,
    func,
    Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship
from sqlalchemy_utils import aggregated

from app.tasks.models import Task
from app.treeitems.models import TreeItem

class Objective(TreeItem):
    id = Column(
        UUID(as_uuid=True),
        ForeignKey("treeitem.id", ondelete="CASCADE"),
        primary_key=True,
        default=uuid.uuid4,
    )
    # belongs to a phase
    phase_id = Column(
        UUID(as_uuid=True), ForeignKey("phase.id", ondelete='CASCADE')
    )
    phase = relationship("Phase", foreign_keys=[phase_id], backref=backref('children', passive_deletes=True))

    # Infered state from tasks

    @aggregated('children', Column(Date))
    def end_date(self):
        return func.max(Task.end_date)

    @aggregated('children', Column(Date))
    def start_date(self):
        return func.min(Task.start_date)

    progress = Column(Numeric, default=0)

    __mapper_args__ = {
        "polymorphic_identity": "objective",
    }

    def __repr__(self):
        return "<Objective %r>" % self.name

    @property
    def coproductionprocess(self):
        return self.phase.coproductionprocess
    
    @property
    def path_ids(self):
        return [self.phase_id, self.id]
    
    @property
    def is_disabled(self):
        return (self.disabled_on is not None) or (self.phase.disabled_on) is not None
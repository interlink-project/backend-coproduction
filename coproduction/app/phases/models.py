import uuid
from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import aggregated

from app.tasks.models import Task
from app.treeitems.models import TreeItem

class Phase(TreeItem):
    id = Column(
        UUID(as_uuid=True),
        ForeignKey("treeitem.id", ondelete="CASCADE"),
        primary_key=True,
        default=uuid.uuid4,
    )
    # they belong to a process
    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = relationship("CoproductionProcess", foreign_keys=[coproductionprocess_id], backref=backref('children', passive_deletes=True))

    # Infered state from objectives
    @aggregated('children', Column(Date))
    def end_date(self):
        return func.max(Task.end_date)

    @aggregated('children', Column(Date))
    def start_date(self):
        return func.min(Task.start_date)

    progress = Column(Numeric, default=0)
    
    __mapper_args__ = {
        "polymorphic_identity": "phase",
    }

    def __repr__(self):
        return "<Phase %r>" % self.name
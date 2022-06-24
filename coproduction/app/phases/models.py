import uuid
from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Numeric,
    Integer,
    func,
    Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import aggregated

from app.objectives.models import Objective
from app.treeitems.models import TreeItem
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

class Phase(TreeItem):
    id = Column(
        UUID(as_uuid=True),
        ForeignKey("treeitem.id", ondelete="CASCADE"),
        primary_key=True,
        default=uuid.uuid4,
    )
    is_part_of_codelivery = Column(Boolean, default=False)

    # they belong to a process
    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = relationship("CoproductionProcess", foreign_keys=[coproductionprocess_id], backref=backref('children', passive_deletes=True))

    # Infered state from objectives
    objectives_ids = association_proxy('children', 'id')

    @aggregated('children', Column(Date))
    def end_date(self):
        return func.max(Objective.end_date)

    @aggregated('children', Column(Date))
    def start_date(self):
        return func.min(Objective.start_date)

    progress = Column(Numeric, default=0)
    
    __mapper_args__ = {
        "polymorphic_identity": "phase",
    }

    @hybrid_property
    def is_disabled(self):
        return (self.disabled_on is not None)

    @hybrid_property
    def path_ids(self):
        return [self.id]

    def __repr__(self):
        return "<Phase %r>" % self.name
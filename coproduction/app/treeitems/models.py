
import enum
import uuid

from sqlalchemy import (
    Boolean,
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
    orm,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_utils import aggregated

from app.general.db.base_class import Base as BaseModel


class Status(enum.Enum):
    awaiting = "awaiting"
    in_progress = "in_progress"
    finished = "finished"

class Types(enum.Enum):
    task = "task"
    objective = "objective"
    phase = "phase"

prerequisites = Table(
    'treeitem_prerequisites', BaseModel.metadata,
    Column('treeitem_a_id', ForeignKey(
        'treeitem.id', ondelete="CASCADE"), primary_key=True),
    Column('treeitem_b_id', ForeignKey(
        'treeitem.id', ondelete="CASCADE"), primary_key=True)
)


class TreeItem(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # created by
    creator_id = Column(String, ForeignKey("user.id", use_alter=True, ondelete='SET NULL'))
    creator = orm.relationship('User', foreign_keys=[creator_id], post_update=True, backref="created_treeitems")

    name = Column(String)
    description = Column(String)
    disabled = Column(Date)
    type = Column(Enum(Types, create_constraint=False,native_enum=False), default=Types.task)

    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = orm.relationship(
        "CoproductionProcess", backref=orm.backref('treeitems', passive_deletes=True))

    # children
    parent_id = Column(UUID(as_uuid=True), ForeignKey("treeitem.id"))
    children = orm.relationship(
        "TreeItem", backref=orm.backref("parent", remote_side=[id])
    )
    children_ids = association_proxy('children', 'id')
    # @aggregated('children', Column(Integer))
    # def children_count(self):
    #     return func.count('1')

    # prerequisites
    prerequisites = orm.relationship("TreeItem", secondary=prerequisites,
                                     primaryjoin=id == prerequisites.c.treeitem_a_id,
                                     secondaryjoin=id == prerequisites.c.treeitem_b_id,
                                     )

    prerequisites_ids = association_proxy('prerequisites', 'id')

    # for tasks
    problemprofiles = Column(ARRAY(String), default=dict)
    status = Column(Enum(Status, create_constraint=False,native_enum=False), default=Status.awaiting)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # @aggregated('children', Column(Date))
    # def agg_start_date(self):
    #     return func.min(TreeItem.start_date)

    # @aggregated('children', Column(Date))
    # def agg_end_date(self):
    #     return func.max(TreeItem.end_date)

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

class TreeItemTypes(str, enum.Enum):
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
    type = Column(String(70))
    # created by
    creator_id = Column(String, ForeignKey("user.id", use_alter=True, ondelete='SET NULL'))
    creator = orm.relationship('User', foreign_keys=[creator_id], post_update=True, backref="created_treeitems")

    name = Column(String)
    description = Column(String)

    disabled_on = Column(Date)
    prerequisites = orm.relationship("TreeItem", secondary=prerequisites,
                                     primaryjoin=id == prerequisites.c.treeitem_a_id,
                                     secondaryjoin=id == prerequisites.c.treeitem_b_id,
                                     )
    prerequisites_ids = association_proxy('prerequisites', 'id')

    __mapper_args__ = {
        "polymorphic_identity": "treeitem",
        "polymorphic_on": type,
    }

class Phase(TreeItem):
    id = Column(
        UUID(as_uuid=True),
        ForeignKey("treeitem.id", ondelete="CASCADE"),
        primary_key=True,
        default=uuid.uuid4,
    )
    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = orm.relationship(
        "CoproductionProcess", backref=orm.backref('treeitems', passive_deletes=True))
    
    __mapper_args__ = {
        "polymorphic_identity": "phase",
    }

    @aggregated('objectives', Column(Date))
    def start_date(self):
        return func.min(Objective.start_date)
    
    @aggregated('objectives', Column(Date))
    def end_date(self):
        return func.max(Objective.end_date)
    


class Objective(TreeItem):
    id = Column(
        UUID(as_uuid=True),
        ForeignKey("treeitem.id", ondelete="CASCADE"),
        primary_key=True,
        default=uuid.uuid4,
    )
    # parent
    phase_id = Column(UUID(as_uuid=True), ForeignKey("phase.id", ondelete='CASCADE'))
    phase = orm.relationship("Phase", backref="objectives")

    @aggregated('tasks', Column(Date))
    def start_date(self):
        return func.min(Task.start_date)
    
    @aggregated('tasks', Column(Date))
    def end_date(self):
        return func.max(Task.end_date)

    __mapper_args__ = {
        "polymorphic_identity": "task",
    }

class Task(TreeItem):
    id = Column(
        UUID(as_uuid=True),
        ForeignKey("treeitem.id", ondelete="CASCADE"),
        primary_key=True,
        default=uuid.uuid4,
    )
    # parent
    objective_id = Column(UUID(as_uuid=True), ForeignKey("objective.id", ondelete='CASCADE'))
    objective = orm.relationship("Objective", backref="tasks")

    problemprofiles = Column(ARRAY(String), default=dict)
    status = Column(Enum(Status, create_constraint=False,native_enum=False), default=Status.awaiting)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "task",
    }
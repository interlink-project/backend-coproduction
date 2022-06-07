import uuid
import enum

from sqlalchemy import Column, ForeignKey, String, Table, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.general.db.base_class import Base as BaseModel

prerequisites = Table(
    'treeitem_prerequisites', BaseModel.metadata,
    Column('treeitem_a_id', ForeignKey(
        'treeitem.id', ondelete="CASCADE"), primary_key=True),
    Column('treeitem_b_id', ForeignKey(
        'treeitem.id', ondelete="CASCADE"), primary_key=True)
)


class Status(enum.Enum):
    awaiting = "awaiting"
    in_progress = "in_progress"
    finished = "finished"


class TreeItem(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(70))
    name = Column(String)
    description = Column(String)
    
    # prerequisites
    prerequisites = relationship("TreeItem", secondary=prerequisites,
                                 primaryjoin=id == prerequisites.c.treeitem_a_id,
                                 secondaryjoin=id == prerequisites.c.treeitem_b_id,
                                 )

    prerequisites_ids = association_proxy('prerequisites', 'id')

    # created by
    creator_id = Column(String, ForeignKey(
        "user.id", use_alter=True, ondelete='SET NULL'))
    creator = relationship('User', foreign_keys=[creator_id], post_update=True, backref="created_treeitems")

    # state
    status = Column(Enum(Status, create_constraint=False, native_enum=False), default=Status.awaiting)
    
    # Disabled by
    # disabler_id = Column(String, ForeignKey(
    #     "user.id", use_alter=True, ondelete='SET NULL'))
    # disabler = relationship('User', foreign_keys=[disabler_id], post_update=True, backref="disabled_treeitems")
    # disabled_on = Column(DateTime)

    __mapper_args__ = {
        "polymorphic_identity": "treeitem",
        "polymorphic_on": type,
    }

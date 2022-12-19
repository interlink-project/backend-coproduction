import uuid

from sqlalchemy import Column, ForeignKey, String, Table, Integer, func, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app.general.db.base_class import Base as BaseModel
from app.config import settings
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_utils import aggregated
from sqlalchemy.orm import Session
from app.utils import ChannelTypes

class Notification(BaseModel):
    """Notification Class contains standard information for a Notification."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event = Column(String, nullable=False)
    message = Column(String, nullable=False)
    channel = Column(Enum(ChannelTypes, create_constraint=False, native_enum=False), nullable=False)
    template = Column(String, nullable=True)
    list_vars = Column(String, nullable=True)
    url_boton = Column(String, nullable=True)
    
    #Resource 
    resource_id = Column(String, ForeignKey(
        "asset.id", use_alter=True, ondelete='SET NULL'),nullable=True)
    resource = relationship('Asset', foreign_keys=[resource_id], post_update=True, backref="notifications")

    #Actor / Sender
    actor_id = Column(String, ForeignKey(
        "user.id", use_alter=True, ondelete='SET NULL'),nullable=True)
    actor = relationship('User', foreign_keys=[actor_id], post_update=True, backref="notifications_sended")

    #Receiver
    notifier_id = Column(String, ForeignKey(
        "user.id", use_alter=True, ondelete='SET NULL'),nullable=True)
    notifier = relationship('User', foreign_keys=[notifier_id], post_update=True, backref="notifications_received")

    state =Column(Boolean,default=False)

    def __repr__(self) -> str:
        return f"<Notification {self.id} {self.event} {self.channel}>"

 
   
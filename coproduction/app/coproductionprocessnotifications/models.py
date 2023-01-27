import uuid

from sqlalchemy import Column, ForeignKey, String, Table, Integer, func, Boolean, Enum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship, declarative_base

from app.general.db.base_class import Base as BaseModel
from app.config import settings
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_utils import aggregated
from sqlalchemy.orm import Session
from app.utils import ChannelTypes
from app.coproductionprocesses.models import CoproductionProcess

class CoproductionProcessNotification(BaseModel):
    """Association Class contains for a Notification and CoproductionProcess."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coproductionprocess_id = Column(UUID(as_uuid=True), ForeignKey("coproductionprocess.id", use_alter=True, ondelete='SET NULL'), nullable=False)
    asset_id = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notification.id", use_alter=True, ondelete='SET NULL'), nullable=False)

    #Json object with information relevant to a notification:
    parameters = Column(JSON, nullable=True)
    
    notification = relationship('Notification', post_update=True, back_populates="coproductionprocesses")
    coproductionprocess = relationship('CoproductionProcess', back_populates="coproductionprocess_notification_associations")
    #asset = relationship('Asset')
    
    def __repr__(self) -> str:
        return f"<CoproductionProcessNotification {self.created_at}>"
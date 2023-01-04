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
from app.teams.models import Team

class TeamNotification(BaseModel):
    """Association Class contains for a Notification and Team."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("team.id", use_alter=True, ondelete='SET NULL'), nullable=False)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notification.id", use_alter=True, ondelete='SET NULL'), nullable=False)

    #Json object with information relevant to a notification:
    parameters = Column(JSON, nullable=True)
    
    notification = relationship('Notification', post_update=True, back_populates="teams")
    team = relationship('Team', back_populates="team_notification_associations")
    
    def __repr__(self) -> str:
        return f"<TeamNotification {self.created_at}>"
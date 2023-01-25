import uuid

from sqlalchemy import Column, ForeignKey, String, Table, Integer, func, Boolean, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship, declarative_base

from app.general.db.base_class import Base as BaseModel
from app.config import settings
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_utils import aggregated
from sqlalchemy.orm import Session
from app.utils import ChannelTypes
from app.users.models import User
from app.config import settings

class Notification(BaseModel):
    """Notification Class contains standard information for a Notification."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event = Column(String, nullable=False)
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    html_template = Column(Text, nullable=True)
    url_link = Column(String, nullable=True)
    icon = Column(String,nullable=True)
    language = Column(String, default=settings.DEFAULT_LANGUAGE)

    users = relationship('UserNotification', back_populates='notification')
    assets = relationship('AssetNotification', back_populates='notification')
    coproductionprocesses = relationship('CoproductionProcessNotification', back_populates='notification')
    teams = relationship('TeamNotification', back_populates='notification')

    def __repr__(self) -> str:
        return f"<Notification {self.id} {self.event} {self.title} {self.subtitle} {self.url_link}>"

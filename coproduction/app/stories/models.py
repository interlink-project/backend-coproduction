import uuid

from sqlalchemy import Date, Column, ForeignKey, String, Table, Integer, func, Boolean, Enum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relationship, declarative_base

from app.general.db.base_class import Base as BaseModel
from app.config import settings
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_utils import aggregated
from sqlalchemy.orm import Session
from app.utils import ChannelTypes
from app.utils import ClaimTypes
from app.coproductionprocesses.models import CoproductionProcess

class Story(BaseModel):
    """Association Class contains for a Notification and CoproductionProcess."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coproductionprocess_id = Column(UUID(as_uuid=True), ForeignKey("coproductionprocess.id", use_alter=True, ondelete='SET NULL'), nullable=False)
    user_id = Column(String, nullable=True)
    state = Column(Boolean, nullable=False, default=False)

    #Json object with information relevant to a story:
    data_story = Column(JSONB, nullable=True)

    rating = Column(Integer)

    coproductionprocess = relationship('CoproductionProcess', back_populates="coproductionprocess_story_associations")
    published_date = Column(Date, nullable=True)
    

    def __repr__(self) -> str:
        return f"<Story {self.created_at}>"
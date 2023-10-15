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
from app.users.models import User

class Claim(BaseModel):
    """Association Class contains for a Notification and User."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        String, ForeignKey("user.id", ondelete='CASCADE')
    )
    user = relationship("User", foreign_keys=[user_id], backref=backref('claims', passive_deletes=True))

    asset_id = Column(
        UUID(as_uuid=True), ForeignKey("asset.id", ondelete='CASCADE')
    )
    asset = relationship("Asset", foreign_keys=[asset_id], backref=backref('claims', passive_deletes=True))
    
    task_id = Column(UUID(as_uuid=True), nullable=True)
    coproductionprocess_id = Column(UUID(as_uuid=True), nullable=True)
    
    # add the foreign key to assignment
    assignment_id = Column(UUID(as_uuid=True), ForeignKey('assignment.id'), nullable=True)

    
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    state = Column(Boolean, nullable=True, default=False)
    claim_type = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<Claim {self.id} {self.user_id} {self.title} {self.state}>"
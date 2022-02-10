import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.general.db.base_class import Base as BaseModel
import requests

class Membership(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        String, ForeignKey("user.id")
    )
    user = relationship("User", back_populates="memberships")
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("team.id")
    )
    team = relationship("Team", back_populates="memberships")

    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', name='_user_team_uc'),
    )

    def __repr__(self) -> str:
        return f"<Membership {self.user.given_name} - {self.team.name}>"
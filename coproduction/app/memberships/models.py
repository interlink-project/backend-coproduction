import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.general.db.base_class import Base as BaseModel


class Membership(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(String)
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("team.id")
    )
    team = relationship("Team", back_populates="memberships")

    def __repr__(self) -> str:
        return f"<Membership {self.user.given_name} - {self.team.name}>"

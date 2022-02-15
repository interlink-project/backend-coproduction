import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.general.db.base_class import Base as BaseModel
from app.coproductionprocesses.models import association_table

class Team(BaseModel):
    """Team Class contains standard information for a Team."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    logotype = Column(String, nullable=True)

    # created by
    creator_id = Column(
        String, ForeignKey("user.id")
    )
    creator = relationship("User", back_populates="created_teams")

    memberships = relationship("Membership", back_populates="team")
    coproductionprocesses = relationship("CoproductionProcess", secondary=association_table, back_populates="teams")

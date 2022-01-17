from app.general.db.base_class import Base as BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Team(BaseModel):
    """Team Class contains standard information for a Team."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String)
    description = Column(String)
    logotype = Column(String)

    memberships = relationship("Membership", back_populates="team")
    coproductionprocesses = relationship("CoproductionProcess", back_populates="team")
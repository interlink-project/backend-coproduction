from app.general.db.base_class import Base as BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(BaseModel):
    """User model that acts as middleware for that on auth microservice. 
    We want to use relational capabilities"""
    id = Column(String, primary_key=True)
    email = Column(String, nullable=False)

    memberships = relationship("Membership", back_populates="user")
    created_coproductionprocesses = relationship("CoproductionProcess", back_populates="creator")
    created_teams = relationship("Team", back_populates="creator")
    created_assets = relationship("Asset", back_populates="creator")

    #TODO property that gets info from auth microservice
    def __repr__(self) -> str:
        return f"<User {self.email}>"
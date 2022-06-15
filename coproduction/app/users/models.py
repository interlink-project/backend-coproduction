from app.general.db.base_class import Base as BaseModel
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy

class User(BaseModel):
    """User model that acts as middleware for that on auth microservice. 
    We want to use relational capabilities"""
    id = Column(String, primary_key=True)
    picture = Column(String)
    full_name = Column(String)
    last_login = Column(DateTime)
    email = Column(String)
    zoneinfo = Column(String)
    locale = Column(String)
    
    teams_ids = association_proxy('teams', 'id')

    #TODO property that gets info from auth microservice
    def __repr__(self) -> str:
        return f"<User {self.id}>"
    
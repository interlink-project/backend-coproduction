from app.general.db.base_class import Base as BaseModel
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.associationproxy import association_proxy

class User(BaseModel):
    id = Column(String, primary_key=True)
    picture = Column(String)
    full_name = Column(String)
    last_login = Column(DateTime)
    email = Column(String)
    zoneinfo = Column(String)
    locale = Column(String)
    
    teams_ids = association_proxy('teams', 'id')
    administered_teams_ids = association_proxy('administered_teams', 'id')

    def __repr__(self) -> str:
        return f"<User {self.id}>"
    
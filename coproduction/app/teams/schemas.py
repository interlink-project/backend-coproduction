import uuid
from typing import Optional, List

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime


class TeamBase(BaseModel):
    name: str
    description: str
    
class TeamCreate(TeamBase):
    user_ids: List[str]


class TeamPatch(TeamBase, metaclass=AllOptional):
    logotype: Optional[str]


class Team(TeamBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    logotype: Optional[str]
    created_by: str
    
    class Config:
        orm_mode = True


class TeamOut(Team):
    pass

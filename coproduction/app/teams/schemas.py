import uuid
from typing import Optional, List

from pydantic import BaseModel, validator
from app.general.utils.AllOptional import AllOptional
from datetime import datetime
from app.config import settings
from app.users.schemas import UserOut

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
    
    #creator: str
    
    class Config:
        orm_mode = True


class TeamOut(Team):
    logotype_link: Optional[str]
    users: Optional[List[UserOut]]
    creator_id: Optional[str]
    type: str
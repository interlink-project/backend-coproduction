import uuid
from typing import Optional, List

from pydantic import BaseModel, validator
from app.general.utils.AllOptional import AllOptional
from datetime import datetime
from app.config import settings

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
    @validator('logotype', pre=True)
    def set_logotype(cls, v):
        if v:
            return settings.COMPLETE_SERVER_NAME + v
        return v

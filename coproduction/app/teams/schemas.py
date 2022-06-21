import uuid
from typing import Optional, List

from pydantic import BaseModel, validator
from app.general.utils.AllOptional import AllOptional
from datetime import datetime
from app.utils import RoleTypes
from app.users.schemas import UserOut

class TeamBase(BaseModel):
    name: str
    description: str
    organization_id: Optional[uuid.UUID]
    public: Optional[bool]
    type: RoleTypes

class TeamCreate(TeamBase):
    user_ids: Optional[List[str]]

class TeamPatch(TeamBase, metaclass=AllOptional):
    logotype: Optional[str]
    type: Optional[RoleTypes]

class Team(TeamBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    logotype: Optional[str]
    
    creator_id: str
    
    class Config:
        orm_mode = True


class TeamOut(Team):
    logotype_link: Optional[str]
    users: Optional[List[UserOut]]
    
    administrators_ids: List[str]
    users_count: Optional[int] = 0
    user_participation: list
    
    @validator('administrators_ids', pre=True)
    def administrators_ids_to_list(cls, v):
        return list(v)
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator
from .models import TeamCreationPermissions
from app.utils import RoleTypes

class OrganizationBase(BaseModel):
    name_translations: dict
    description_translations: Optional[dict]
    icon: Optional[str]
    logotype: Optional[str]
    default_team_type: RoleTypes
    team_creation_permission: Optional[TeamCreationPermissions]
    public: Optional[bool]
    
class OrganizationCreate(OrganizationBase):
    pass

class OrganizationPatch(OrganizationCreate):
    name_translations: Optional[dict]
    default_team_type: Optional[RoleTypes]

class Organization(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    name: str
    description: Optional[str]
    creator_id: Optional[str]

    class Config:
        orm_mode = True


class OrganizationOut(Organization):
    icon_link: Optional[str] 
    logotype_link: Optional[str] 
    administrators_ids: List[str]
    teams_ids: List[uuid.UUID]
    user_participation: list
    people_involved: int
    
    @validator('administrators_ids', pre=True)
    def administrators_ids_to_list(cls, v):
        return list(v)
    
    @validator('teams_ids', pre=True)
    def teams_ids_to_list(cls, v):
        return list(v)

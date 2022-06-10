import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from .models import OrganizationTypes

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str]
    logotype: Optional[str]
    type: OrganizationTypes
    
class OrganizationCreate(OrganizationBase):
    pass

class OrganizationPatch(OrganizationCreate):
    name:  Optional[str]

class Organization(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class OrganizationOut(Organization):
    logotype_link: Optional[str] 

import uuid
from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, validator
from .models import Status

class TreeItemCreate(BaseModel):
    name: str
    description: str
    from_schema: Optional[uuid.UUID]
    from_item: Optional[uuid.UUID]

class TreeItemPatch(BaseModel):
    name: Optional[str]
    description: Optional[str]
    disabler_id: Optional[str]
    disabled_on: Optional[datetime]

class TreeItem(TreeItemCreate):
    id: uuid.UUID
    type: str
    created_at: datetime
    updated_at: Optional[datetime]
    prerequisites_ids: List[uuid.UUID]
    
    start_date: Optional[date]
    end_date: Optional[date]
    status: Optional[Status]
    progress: Optional[int]
    
    creator_id: Optional[str]
    disabler_id: Optional[str]
    disabled_on: Optional[datetime]

    path_ids: List[uuid.UUID]
    is_disabled: bool

    @validator('prerequisites_ids', pre=True)
    def prerequisites_ids_to_list(cls, v):
        return list(v)

    class Config:
        orm_mode = True


class TreeItemOut(TreeItem):
    pass
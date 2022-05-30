import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, validator
from .models import TreeItemTypes

class TreeItemBase(BaseModel):
    name: str
    description: str
    coproductionprocess_id: Optional[uuid.UUID]
    parent_id: Optional[uuid.UUID]
    type: TreeItemTypes

class TreeItemCreate(TreeItemBase):
    
    problemprofiles: Optional[list]
    status: Optional[str]
    _start_date: Optional[date]
    _end_date: Optional[date]


class TreeItemPatch(TreeItemBase):
    problemprofiles: Optional[list]
    status: Optional[str]
    _start_date: Optional[date]
    _end_date: Optional[date]


class TreeItem(TreeItemBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    start_date: Optional[date]
    end_date: Optional[date]

    status: Optional[Enum]
    progress: Optional[int]

    class Config:
        orm_mode = True


class TreeItemOut(TreeItem):
    problemprofiles: list
    children_ids: List[uuid.UUID]
    prerequisites_ids: List[uuid.UUID]

    @validator('prerequisites_ids', pre=True)
    def prerequisites_ids_to_list(cls, v):
        return list(v)

    @validator('children_ids', pre=True)
    def children_ids_to_list(cls, v):
        return list(v)

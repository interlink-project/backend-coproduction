from enum import Enum
import uuid
from datetime import datetime, date
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel, validator
from .models import Status

class TreeItemCreate(BaseModel):
    name: str
    description: str

class TreeItemPatch(BaseModel):
    name: Optional[str]
    description: Optional[str]

class TreeItem(TreeItemCreate):
    id: uuid.UUID
    type: str
    created_at: datetime
    updated_at: Optional[datetime]

    start_date: Optional[date]
    end_date: Optional[date]
    status: Optional[Status]
    progress: Optional[int]

    creator_id: Optional[uuid.UUID]

    class Config:
        orm_mode = True


class TreeItemOut(TreeItem):
    prerequisites_ids: List[uuid.UUID]

    @validator('prerequisites_ids', pre=True)
    def prerequisites_ids_to_list(cls, v):
        return list(v)
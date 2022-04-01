from enum import Enum
import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel


class TaskBase(BaseModel):
    problemprofiles: list
    name: str
    description: str
    start_date: Optional[date]
    end_date: Optional[date]
    objective_id: uuid.UUID

class TaskCreate(TaskBase):
    objective_id: Optional[uuid.UUID]

class TaskPatch(TaskBase):
    problemprofiles: Optional[list]
    objective_id: Optional[uuid.UUID]
    status: Optional[str]
    name: Optional[str]
    description: Optional[str]


class Task(TaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    status: Optional[Enum]

    class Config:
        orm_mode = True


class TaskOut(Task):
    prerequisites_ids: List[uuid.UUID]

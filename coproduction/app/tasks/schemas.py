import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.general.utils.AllOptional import AllOptional


class TaskBase(BaseModel):
    is_public: bool = True

    objective_id: uuid.UUID
    parent_id: Optional[uuid.UUID]


class TaskCreate(TaskBase):
    name_translations: dict
    description_translations: dict


class TaskPatch(TaskBase, metaclass=AllOptional):
    pass


class Task(TaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    name: str
    description: str

    class Config:
        orm_mode = True


class TaskOut(Task):
    # parent
    pass

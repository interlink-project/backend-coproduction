from enum import Enum
import uuid
from datetime import datetime
from typing import List, Optional

import requests
from pydantic import BaseModel, validator

from app.config import settings
from app.general.utils.AllOptional import AllOptional


class TaskBase(BaseModel):
    is_public: bool = True
    problem_profiles: list

    objective_id: uuid.UUID
    parent_id: Optional[uuid.UUID]


class TaskCreate(TaskBase):
    name_translations: dict
    description_translations: dict
    
    @validator('problem_profiles')
    def problem_profiles_valid(cls, v, values, **kwargs):
        problem_profiles_ids = requests.get(
            f"http://{settings.CATALOGUE_SERVICE_NAME}/api/v1/problemprofiles/ids").json()
        for id in v:
            if id not in problem_profiles_ids:
                raise ValueError(f'Invalid problem profile id {id}')
        return v


class TaskPatch(TaskBase):
    is_public: Optional[bool]
    problem_profiles: Optional[list]

    objective_id: Optional[uuid.UUID]
    name_translations: Optional[dict]
    description_translations: Optional[dict]
    status: Optional[str]


class Task(TaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    name: str
    description: str
    status: Optional[Enum]

    class Config:
        orm_mode = True


class TaskOut(Task):
    # parent
    pass

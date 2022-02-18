from enum import Enum
import uuid
from datetime import datetime
from typing import List, Optional

import requests
from pydantic import BaseModel, validator

from app.config import settings
from app.general.utils.AllOptional import AllOptional



class TaskMetadataBase(BaseModel):
    problem_profiles: list
    objectivemetadata_id: uuid.UUID


class TaskMetadataCreate(TaskMetadataBase):
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


class TaskMetadataPatch(TaskMetadataBase):
    problem_profiles: Optional[list]

    objectivemetadata_id: Optional[uuid.UUID]
    name_translations: Optional[dict]
    description_translations: Optional[dict]


class TaskMetadata(TaskMetadataBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    name: str
    description: str

    class Config:
        orm_mode = True


class TaskMetadataOut(TaskMetadata):
    # parent
    pass

###

class TaskBase(BaseModel):
    problem_profiles: list
    name: str
    description: str
    objective_id: uuid.UUID


class TaskCreate(TaskBase):
    name_translations: dict
    description_translations: dict

class TaskPatch(TaskBase):
    problem_profiles: Optional[list]
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
    # parent
    pass

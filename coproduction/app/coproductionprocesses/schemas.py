import uuid
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, validator

from app.config import settings
from app.permissions.schemas import PermissionOut
from pydantic_choices import choice
from .models import Status

Languages = choice(settings.ALLOWED_LANGUAGES_LIST)

class CoproductionProcessBase(BaseModel):
    schema_used: Optional[uuid.UUID]
    name: str
    description: Optional[str]
    aim: Optional[str]
    idea: Optional[str]
    organization_desc: Optional[str]
    organization_id: Optional[uuid.UUID]
    challenges: Optional[str]
    status: Optional[Status]
    incentive_and_rewards_state:Optional[bool]

class CoproductionProcessCreate(CoproductionProcessBase):
    language: Languages

    class Config:
        arbitrary_types_allowed = True

class CoproductionProcessPatch(CoproductionProcessCreate):
    name:  Optional[str]
    status: Optional[Status]
    logotype: Optional[str]
    incentive_and_rewards_state:Optional[bool]
    language: Optional[Languages]


class CoproductionProcess(CoproductionProcessBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    logotype: Optional[str]
    creator_id: str

    class Config:
        orm_mode = True


class CoproductionProcessOut(CoproductionProcess):
    logotype_link: Optional[str] 
    language: Any
    administrators_ids: List[str]
    current_user_participation: list

    @validator('administrators_ids', pre=True)
    def administrators_ids_to_list(cls, v):
        return list(v)
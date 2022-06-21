import uuid
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, validator

from app.config import settings
from app.permissions.schemas import PermissionOut
from pydantic_choices import choice

Languages = choice(settings.ALLOWED_LANGUAGES_LIST)

class CoproductionProcessBase(BaseModel):
    schema_used: Optional[uuid.UUID]
    name: str
    description: Optional[str]
    aim: Optional[str]
    idea: Optional[str]
    organization_id: Optional[uuid.UUID]
    challenges: Optional[str]

class CoproductionProcessCreate(CoproductionProcessBase):
    language: Languages

    class Config:
        arbitrary_types_allowed = True

class CoproductionProcessPatch(CoproductionProcessCreate):
    name:  Optional[str]
    logotype: Optional[str]
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
    permissions: List[PermissionOut]
    administrators_ids: List[str]
    user_participation: list

    @validator('administrators_ids', pre=True)
    def administrators_ids_to_list(cls, v):
        return list(v)
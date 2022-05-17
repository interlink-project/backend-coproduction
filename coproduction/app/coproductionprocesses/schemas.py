import uuid
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from app.config import settings
from app.roles.schemas import RoleBase
from pydantic_choices import choice

Languages = choice(settings.ALLOWED_LANGUAGES_LIST)

class CoproductionProcessBase(BaseModel):
    name: str
    description: Optional[str]
    aim: Optional[str]
    idea: Optional[str]
    organization: Optional[str]
    challenges: Optional[str]

class CoproductionProcessCreate(CoproductionProcessBase):
    language: Languages
    team_id: Optional[uuid.UUID]
    roles: Optional[List[RoleBase]]

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
    phases_count: Optional[int]
    logotype_link: Optional[str] 
    language: Any
import uuid
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, validator
from typing_extensions import Annotated

from app.config import settings
from app.general.utils.AllOptional import AllOptional
from app.roles.schemas import RoleBase, RoleOut, ExceptionOut

class CoproductionProcessBase(BaseModel):
    name: str
    description: Optional[str]
    aim: Optional[str]
    idea: Optional[str]
    organization: Optional[str]
    challenges: Optional[str]

    artefact_id: Optional[uuid.UUID]

class CoproductionProcessCreate(CoproductionProcessBase):
    team_id: uuid.UUID
    roles: Optional[List[RoleBase]]

    class Config:
        arbitrary_types_allowed = True

class CoproductionProcessPatch(CoproductionProcessCreate):
    name:  Optional[str]
    team_id: Optional[uuid.UUID]
    logotype: Optional[str]


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
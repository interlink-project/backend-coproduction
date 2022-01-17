import uuid
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from app.general.utils.AllOptional import AllOptional

class CoproductionProcessBase(BaseModel):
    name: str
    description: Optional[str]
    logotype: Optional[str]
    aim: Optional[str]
    idea: Optional[str]
    organization: Optional[str]
    challenges: Optional[str]

class CoproductionProcessCreate(CoproductionProcessBase):
    artefact_id: Optional[uuid.UUID]
    schema_id: Optional[uuid.UUID]
    team_id: uuid.UUID


class CoproductionProcessPatch(CoproductionProcessCreate, metaclass=AllOptional):
    pass


class CoproductionProcess(CoproductionProcessBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class CoproductionProcessOut(CoproductionProcess):
    artefact_id: Optional[uuid.UUID]
    team_id: uuid.UUID

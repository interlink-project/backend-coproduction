import uuid
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from app.general.utils.AllOptional import AllOptional

class CoproductionProcessBase(BaseModel):
    name: str
    description: Optional[str]
    aim: Optional[str]
    idea: Optional[str]
    organization: Optional[str]
    challenges: Optional[str]

    artefact_id: Optional[uuid.UUID]
    coproductionschema_id: Optional[uuid.UUID]
    team_id: uuid.UUID

class CoproductionProcessCreate(CoproductionProcessBase):
    pass

class CoproductionProcessPatch(CoproductionProcessCreate, metaclass=AllOptional):
    logotype: Optional[str]


class CoproductionProcess(CoproductionProcessBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    logotype: Optional[str]
    # creator: str
    
    class Config:
        orm_mode = True


class CoproductionProcessOut(CoproductionProcess):
    pass

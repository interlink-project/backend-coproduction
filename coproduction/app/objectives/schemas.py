from enum import Enum
import uuid
from datetime import datetime, date
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class ObjectiveBase(BaseModel):
    progress: Optional[int]
    name: str
    description: str
    phase_id: uuid.UUID
    
class ObjectiveCreate(ObjectiveBase):
    phase_id: Optional[uuid.UUID]


class ObjectivePatch(ObjectiveBase, metaclass=AllOptional):
    pass

class ObjectiveInternalPatch(ObjectiveBase, metaclass=AllOptional):
    status: Optional[Enum]
    progress: Optional[int]

class Objective(ObjectiveBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    start_date: Optional[date]
    end_date: Optional[date]
    
    status: Optional[Enum]
    progress: Optional[int]

    class Config:
        orm_mode = True


class ObjectiveOut(Objective):
    prerequisites_ids: List[uuid.UUID]
import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from app.general.utils.AllOptional import AllOptional

class PhaseBase(BaseModel):
    coproductionprocess_id: uuid.UUID
    name: str
    description: str


class PhaseCreate(PhaseBase):
    pass

class PhaseInternalPatch(PhaseBase, metaclass=AllOptional):
    status: Optional[Enum]
    progress: Optional[int]

class PhasePatch(PhaseBase, metaclass=AllOptional):
    pass


class Phase(PhaseBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    start_date: Optional[date]
    end_date: Optional[date]
    
    status: Optional[Enum]
    progress: Optional[int]
    
    class Config:
        orm_mode = True


class PhaseOut(Phase):
    prerequisites_ids: List[uuid.UUID]

import uuid
from datetime import date, datetime
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class PhaseBase(BaseModel):
    name: str
    is_public: bool
    description: str

class PhaseCreate(PhaseBase):
    pass


class PhasePatch(PhaseBase, metaclass=AllOptional):
    pass


class Phase(PhaseBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class PhaseOut(Phase):
    pass

####

class PhaseInstantiationBase(BaseModel):
    phase_id: uuid.UUID
    coproductionprocess_id: uuid.UUID


class PhaseInstantiationCreate(PhaseInstantiationBase):
    pass


class PhaseInstantiationPatch(PhaseInstantiationBase, metaclass=AllOptional):
    pass


class PhaseInstantiation(PhaseInstantiationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class PhaseInstantiationOut(PhaseInstantiation):
    name: str
    description: str
    progress: int
    start_date: Optional[date]
    end_date: Optional[date]
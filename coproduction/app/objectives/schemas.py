import uuid
from datetime import datetime, date
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class ObjectiveBase(BaseModel):
    name: str
    is_public: bool
    description: str
    phase_id: uuid.UUID

class ObjectiveCreate(ObjectiveBase):
    pass


class ObjectivePatch(ObjectiveBase, metaclass=AllOptional):
    pass


class Objective(ObjectiveBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class ObjectiveOut(Objective):
    pass

####

class ObjectiveInstantiationBase(BaseModel):
    objective_id: uuid.UUID
    phaseinstantiation_id: uuid.UUID
    progress: Optional[int]
    start_date: Optional[date]
    end_date: Optional[date]


class ObjectiveInstantiationCreate(ObjectiveInstantiationBase):
    pass


class ObjectiveInstantiationPatch(ObjectiveInstantiationBase, metaclass=AllOptional):
    pass


class ObjectiveInstantiation(ObjectiveInstantiationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ObjectiveInstantiationOut(ObjectiveInstantiation):
    name: str
    description: str
    start_date: Optional[date]
    end_date: Optional[date]
    tasks_length: int
    progress: int

import uuid
from datetime import datetime, date
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class ObjectiveBase(BaseModel):
    is_public: bool = True
    progress: Optional[int]
    start_date: Optional[date]
    end_date: Optional[date]

    phase_id: uuid.UUID
    parent_id: Optional[uuid.UUID]

class ObjectiveCreate(ObjectiveBase):
    name_translations: dict
    description_translations: dict


class ObjectivePatch(ObjectiveBase, metaclass=AllOptional):
    pass


class Objective(ObjectiveBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    name: str
    description: str

    class Config:
        orm_mode = True


class ObjectiveOut(Objective):
    pass
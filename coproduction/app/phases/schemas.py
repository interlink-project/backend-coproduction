import uuid
from datetime import date, datetime
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class PhaseBase(BaseModel):
    is_public: bool = True

    coproductionprocess_id: Optional[uuid.UUID]
    coproductionschema_id: Optional[uuid.UUID]
    parent_id: Optional[uuid.UUID]

class PhaseCreate(PhaseBase):
    name_translations: dict
    description_translations: dict


class PhasePatch(PhaseBase, metaclass=AllOptional):
    pass


class Phase(PhaseBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    name: str
    description: str

    class Config:
        orm_mode = True


class PhaseOut(Phase):
    # parent
    progress: int
    start_date: Optional[date]
    end_date: Optional[date]
    prerequisites_ids: List[uuid.UUID]
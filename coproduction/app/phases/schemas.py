import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from app.general.utils.AllOptional import AllOptional

#


class PhaseMetadataBase(BaseModel):
    is_public: bool = True
    coproductionschema_id: uuid.UUID


class PhaseMetadataCreate(PhaseMetadataBase):
    name_translations: dict
    description_translations: dict


class PhaseMetadataPatch(PhaseMetadataBase, metaclass=AllOptional):
    pass


class PhaseMetadata(PhaseMetadataBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    name: str
    description: str

    class Config:
        orm_mode = True


class PhaseMetadataOut(PhaseMetadata):
    # parent
    prerequisites_ids: List[uuid.UUID]

###########


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

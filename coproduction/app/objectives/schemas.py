import uuid
from datetime import datetime, date
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class ObjectiveMetadataBase(BaseModel):
    phasemetadata_id: uuid.UUID

class ObjectiveMetadataCreate(ObjectiveMetadataBase):
    name_translations: dict
    description_translations: dict


class ObjectiveMetadataPatch(ObjectiveMetadataBase, metaclass=AllOptional):
    pass


class ObjectiveMetadata(ObjectiveMetadataBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    name: str
    description: str

    class Config:
        orm_mode = True


class ObjectiveMetadataOut(ObjectiveMetadata):
    pass

######

class ObjectiveBase(BaseModel):
    progress: Optional[int]
    start_date: Optional[date]
    end_date: Optional[date]
    name: str
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
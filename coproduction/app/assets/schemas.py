import uuid
from datetime import datetime
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class AssetBase(BaseModel):
    taskinstantiation_id: uuid.UUID
    interlinker_id: uuid.UUID
    external_id: str
    
class AssetCreate(AssetBase):
    pass

class AssetPatch(AssetBase, metaclass=AllOptional):
    pass


class Asset(AssetBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class AssetOut(Asset):
    file_metadata: Optional[dict]
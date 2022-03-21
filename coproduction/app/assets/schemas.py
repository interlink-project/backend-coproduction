import uuid
from datetime import datetime
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class AssetBase(BaseModel):
    task_id: Optional[uuid.UUID]
    softwareinterlinker_id: uuid.UUID
    knowledgeinterlinker_id: Optional[uuid.UUID]
    external_asset_id: str
    
class AssetCreate(AssetBase):
    pass

class AssetPatch(AssetBase, metaclass=AllOptional):
    pass


class Asset(AssetBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    capabilities: Optional[dict]
    interlinker_data: dict
    
    class Config:
        orm_mode = True


class AssetOut(Asset):
    link: str
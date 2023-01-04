import uuid
from typing import Optional, List

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime
from app.utils import ChannelTypes

class AssetNotificationBase(BaseModel):
    asset_id: uuid.UUID
    notification_id: uuid.UUID
    parameters: Optional[str]
 


class AssetNotification(AssetNotificationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class AssetNotificationOut(AssetNotification):
    pass

class AssetNotificationPatch(AssetNotificationBase):
    pass

class AssetNotificationCreate(AssetNotificationBase):
    pass
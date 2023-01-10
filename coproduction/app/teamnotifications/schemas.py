import uuid
from typing import Optional, List

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime
from app.utils import ChannelTypes

class TeamNotificationBase(BaseModel):
    team_id: uuid.UUID
    notification_id: uuid.UUID
    parameters: Optional[str]
 


class TeamNotification(TeamNotificationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class TeamNotificationOut(TeamNotification):
    pass

class TeamNotificationPatch(TeamNotificationBase):
    pass

class TeamNotificationCreate(TeamNotificationBase):
    pass
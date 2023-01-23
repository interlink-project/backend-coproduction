import uuid
from typing import Optional, List

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime
from app.utils import ChannelTypes

class CoproductionProcessNotificationBase(BaseModel):
    coproductionprocess_id: uuid.UUID
    notification_id: uuid.UUID
    parameters: Optional[str]
 


class CoproductionProcessNotification(CoproductionProcessNotificationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class CoproductionProcessNotificationCreatebyEvent(BaseModel):
    coproductionprocess_id: uuid.UUID
    notification_event: str
    parameters: Optional[str]
 



class CoproductionProcessNotificationOut(CoproductionProcessNotification):
    pass

class CoproductionProcessNotificationPatch(CoproductionProcessNotificationBase):
    pass

class CoproductionProcessNotificationCreate(CoproductionProcessNotificationBase):
    pass
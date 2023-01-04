import uuid
from typing import Optional, List

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime
from app.utils import ChannelTypes


class NotificationBase(BaseModel):
    event : str
    title : str
    subtitle : Optional[str]
    text : str
    html_template : Optional[str]
    url_link : Optional[str]



class Notification(NotificationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True



class NotificationOut(Notification):
    pass

class NotificationPatch(NotificationBase):
    pass

class NotificationCreate(NotificationBase):
    pass

import uuid
from typing import Optional, List, Any

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime
from app.utils import ChannelTypes

from pydantic_choices import choice
from app.config import settings
Languages = choice(settings.ALLOWED_LANGUAGES_LIST)

class NotificationBase(BaseModel):
    event : str
    title : str
    subtitle : Optional[str]
    text : str
    html_template : Optional[str]
    url_link : Optional[str]
    icon : Optional[str]



class Notification(NotificationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True



class NotificationOut(Notification):
    language: Any

class NotificationPatch(NotificationBase):
    language: Optional[Languages]

class NotificationCreate(NotificationBase):
    language: Languages

    class Config:
        arbitrary_types_allowed = True

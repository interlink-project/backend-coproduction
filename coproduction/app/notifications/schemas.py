import uuid
from typing import Optional, List

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime
from app.utils import ChannelTypes


class NotificationBase(BaseModel):
   
    event : str
    message : str
    channel : ChannelTypes
    template : Optional[str]
    list_vars : Optional[str]
    url_boton : Optional[str]
    
    #Resource
    resource_id : Optional[str]

    #Actor
    actor_id : Optional[str]
    notifier_id : Optional[str]
    state : Optional[bool]



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


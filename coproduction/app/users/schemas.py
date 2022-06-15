from typing import List, Optional
import uuid
from pydantic import BaseModel, validator
from datetime import datetime
from app.general.utils.AllOptional import AllOptional


class UserBase(BaseModel):
    id: str
    picture: Optional[str]
    full_name: Optional[str]
    last_login: datetime = datetime.now()
    email: Optional[str]
    zoneinfo: Optional[str]
    locale: Optional[str]

class UserCreate(UserBase):
    pass
    
class UserPatch(UserCreate, metaclass=AllOptional):
    pass


class User(UserBase):
    id: str

    class Config:
        orm_mode = True


class UserOut(User):
    teams_ids: List[uuid.UUID]

    @validator('teams_ids', pre=True)
    def teams_ids_to_list(cls, v):
        return list(v)

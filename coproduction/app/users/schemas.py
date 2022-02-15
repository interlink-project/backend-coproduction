import uuid
from typing import Optional, List

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime


class UserBase(BaseModel):
    pass
    
class UserCreate(UserBase):
    id: str

class UserPatch(UserCreate, metaclass=AllOptional):
    pass

class User(UserBase):
    id: str
    class Config:
        orm_mode = True


class UserOut(User):
    pass
import uuid
from typing import Optional, List

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime


class UserBase(BaseModel):
    id: str
    email: str
    
class UserCreate(UserBase):
    pass

class UserPatch(UserBase, metaclass=AllOptional):
    pass

class User(UserBase):
    
    class Config:
        orm_mode = True


class UserOut(User):
    pass
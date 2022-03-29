from pydantic import BaseModel

from app.general.utils.AllOptional import AllOptional


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

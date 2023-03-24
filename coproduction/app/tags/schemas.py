import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TagBase(BaseModel):
    id: uuid.UUID


class TagCreate(TagBase):
    name_translations: dict
    description_translations: dict



class TagPatch(TagCreate):
    pass


class Tag(TagBase):
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class TagOut(Tag):
    pass
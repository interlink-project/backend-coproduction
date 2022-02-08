import uuid
from typing import Optional

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime


class TeamBase(BaseModel):
    logotype: str


class TeamCreate(TeamBase):
    name_translations: dict
    description_translations: dict


class TeamPatch(TeamBase, metaclass=AllOptional):
    pass


class Team(TeamBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    name: str
    description: str
    
    class Config:
        orm_mode = True


class TeamOut(Team):
    pass

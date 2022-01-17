import uuid
from typing import Optional

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime


class TeamBase(BaseModel):
    name: str
    description: str
    logotype: str


class TeamCreate(TeamBase):
    pass


class TeamPatch(TeamBase, metaclass=AllOptional):
    pass


class Team(TeamBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class TeamOut(Team):
    pass

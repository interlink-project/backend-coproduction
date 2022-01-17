import uuid
from typing import Optional

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional
from datetime import datetime

class MembershipBase(BaseModel):
    team_id: uuid.UUID
    user_id: str


class MembershipCreate(MembershipBase):
    pass


class MembershipPatch(MembershipBase, metaclass=AllOptional):
    pass


class Membership(MembershipBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class MembershipOut(Membership):
    pass
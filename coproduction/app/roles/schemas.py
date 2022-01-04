import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from app.general.utils.AllOptional import AllOptional

class RoleBase(BaseModel):
    role: str
    type: str
    user_id: str
    coproductionprocess_id: uuid.UUID

class RoleCreate(RoleBase):
    pass


class RolePatch(RoleCreate, metaclass=AllOptional):
    pass


class Role(RoleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class RoleOut(Role):
    pass

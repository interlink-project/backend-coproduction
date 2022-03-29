from distutils.command import config
import uuid
from datetime import datetime
from typing import Any, List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class ExceptionBase(BaseModel):
    permission: Any
    grant: bool

class ExceptionCreate(ExceptionBase):
    coproductionprocess_id: uuid.UUID
    role_id: uuid.UUID
    # asset_id

class ExceptionPatch(ExceptionCreate, metaclass=AllOptional):
    pass


class Exception(ExceptionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ExceptionOut(Exception):
    pass

###
    
class RoleBase(BaseModel):
    name: str
    description: str
    permissions: Optional[List[Any]]

class RoleCreate(RoleBase):
    coproductionprocess_id: uuid.UUID

class RolePatch(BaseModel):
    name: Optional[str]
    description: Optional[str]
    permissions: Optional[List[Any]]

class Role(RoleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    # team_ids: List[uuid.UUID]
    # user_ids: List[str]

    perms_editable: bool
    meta_editable: bool
    deletable: bool
    selectable: bool

    class Config:
        orm_mode = True


class RoleOut(Role):
    coproductionprocess_id: uuid.UUID
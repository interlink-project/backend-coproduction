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
    acl_id: uuid.UUID
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
    permissions: List[Any]

class RoleCreate(RoleBase):
    acl_id: uuid.UUID

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

#########

class ACLBase(BaseModel):
    coproductionprocess_id: uuid.UUID
    
class ACLCreate(ACLBase):
    roles: Optional[List[RoleBase]]

    class Config:
        arbitrary_types_allowed = True

class ACLPatch(ACLBase, metaclass=AllOptional):
    pass


class ACL(ACLBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class ACLOut(ACL):
    roles: List[RoleOut]
    exceptions: List[ExceptionOut]
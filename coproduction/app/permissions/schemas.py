import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class PermissionBase(BaseModel):
    edit_treeitem_permission: Optional[bool]
    delete_treeitem_permission: Optional[bool]
    view_assets_permission: Optional[bool]
    create_assets_permission: Optional[bool]
    delete_assets_permission: Optional[bool]

class PermissionCreate(PermissionBase):
    user_id: Optional[uuid.UUID]
    team_id: Optional[uuid.UUID]

    treeitem_id: uuid.UUID
    coproductionprocess_id: uuid.UUID

class PermissionPatch(BaseModel):
    pass

class Permission(PermissionCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class PermissionOut(Permission):
    pass
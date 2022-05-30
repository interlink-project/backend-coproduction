from typing import List, Optional

from app.assets.schemas import *
from app.coproductionprocesses.schemas import *
from app.roles.schemas import *
from app.teams.schemas import *
from app.users.schemas import *
from app.treeitems.schemas import *


class BaseORM(BaseModel):
    class Config:
        orm_mode = True


class UserOutFull(UserOut):
    pass


class AssetOutFull(AssetOut):
    pass


class TeamOutFull(TeamOut):
    roles: Optional[List[RoleOut]]


class CoproductionProcessOutFull(CoproductionProcessOut):
    # teams: Optional[List[TeamOutFull]]
    default_role_id: uuid.UUID
    # roles: List[RoleOut]
    exceptions: List[ExceptionOut]


class RoleOutFull(RoleOut):
    users: List[UserOutFull]
    teams: List[TeamOutFull]

class TreeItemOutFull(TreeItemOut):
    children: List["TreeItemOutFull"]

TreeItemOutFull.update_forward_refs()

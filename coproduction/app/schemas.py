from typing import List, Optional

from app.assets.schemas import *
from app.coproductionprocesses.schemas import *
from app.objectives.schemas import *
from app.organizations.schemas import *
from app.permissions.schemas import *
from app.phases.schemas import *
from app.tasks.schemas import *
from app.teams.schemas import *
from app.users.schemas import *


class BaseORM(BaseModel):
    class Config:
        orm_mode = True


class UserOutFull(UserOut):
    pass


class AssetOutFull(AssetOut):
    pass


class OrganizationOutFull(OrganizationOut):
    pass


class TeamOutFull(TeamOut):
    organization: OrganizationOut


class PermissionOutFull(PermissionOut):
    team: TeamOut


class TreeItemOutFull(TreeItemOut):
    permissions: List[PermissionOut]
    user_permissions: dict


class TaskOutFull(TaskOut, TreeItemOutFull):
    pass


class ObjectiveOutFull(ObjectiveOut, TreeItemOutFull):
    children: List[TaskOutFull]


class PhaseOutFull(PhaseOut, TreeItemOutFull):
    children: List[ObjectiveOutFull]


class CoproductionProcessOutFull(CoproductionProcessOut):
    pass

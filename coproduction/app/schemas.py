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
from app.notifications.schemas import *

# out


class UserOutFull(UserOut):
    pass


class AssetOutFull(AssetOut):
    pass


class TeamOutFull(TeamOut):
    # organization: OrganizationOut
    administrators: List[UserOut]


class OrganizationOutFull(OrganizationOut):
    administrators: List[UserOut]
    teams: List[TeamOut]


class PermissionOutFull(PermissionOut):
    team: TeamOut


class TreeItemOutFull(TreeItemOut):
    permissions: List[PermissionOutFull]
    teams: List[TeamOut]


class TaskOutFull(TaskOut, TreeItemOutFull):
    pass


class NotificationOutFull(NotificationOut):
    pass

class ObjectiveOutFull(ObjectiveOut, TreeItemOutFull):
    children: List[TaskOutFull]


class PhaseOutFull(PhaseOut, TreeItemOutFull):
    children: List[ObjectiveOutFull]


class CoproductionProcessOutFull(CoproductionProcessOut):
    enabled_teams: List[TeamOut]
    enabled_permissions: List[PermissionOutFull]
    administrators: List[UserOut]

    @validator('enabled_teams', pre=True)
    def enabled_teams_to_list(cls, v):
        # set instead of list to avoid repeated teams
        return set(v)

# in


class UserIn(BaseModel):
    user_id: str

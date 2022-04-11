from typing import List, Optional

from app.assets.schemas import *
from app.coproductionprocesses.schemas import *
from app.objectives.schemas import *
from app.phases.schemas import *
from app.roles.schemas import *
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


class TaskOutFull(TaskOut):
    # assets: Optional[List[AssetOutFull]]
    pass


class ObjectiveOutFull(ObjectiveOut):
    tasks: List[TaskOutFull]


class PhaseOutFull(PhaseOut):
    objectives: List[ObjectiveOutFull]


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

from typing import List, Optional

from app.acl.schemas import *
from app.assets.schemas import *
from app.coproductionprocesses.schemas import *
from app.coproductionschemas.schemas import *
from app.memberships.schemas import *
from app.objectives.schemas import *
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


class TaskOutFull(TaskOut):
    # assets: Optional[List[AssetOutFull]]
    pass


class TaskMetadataOutFull(TaskMetadataOut):
    pass


class ObjectiveOutFull(ObjectiveOut):
    tasks: List[TaskOutFull]


class ObjectiveMetadataOutFull(ObjectiveMetadataOut):
    taskmetadatas: List[TaskMetadataOutFull] = []


class PhaseOutFull(PhaseOut):
    objectives: List[ObjectiveOutFull]


class PhaseMetadataOutFull(PhaseMetadataOut):
    objectivemetadatas: List[ObjectiveMetadataOutFull] = []


class MembershipOutFull(MembershipOut):
    pass


class TeamOutFull(TeamOut):
    memberships: Optional[List[MembershipOutFull]]


class ACLOutFull(ACLOut):
    default_role_id: uuid.UUID


class CoproductionSchemaOutFull(CoproductionSchemaOut):
    phasemetadatas: List[PhaseMetadataOutFull] = []


class CoproductionProcessOutFull(CoproductionProcessOut):
    teams: Optional[List[TeamOutFull]]

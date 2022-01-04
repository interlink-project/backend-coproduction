from typing import List, Optional

from app.objectives.schemas import *
from app.assets.schemas import *
from app.coproductionprocesses.schemas import *
from app.coproductionschemas.schemas import *
from app.phases.schemas import *
from app.tasks.schemas import *
from app.roles.schemas import *

class BaseORM(BaseModel):
    class Config:
        orm_mode = True


class AssetOutFull(AssetOut):
    pass

class TaskOutFull(TaskOut):
    pass

class TaskInstantiationOutFull(TaskInstantiationOut):
    assets: Optional[List[AssetOutFull]]


class ObjectiveOutFull(ObjectiveOut):
    tasks: List[TaskOutFull]


class ObjectiveInstantiationOutFull(ObjectiveInstantiationOut):
    taskinstantiations: List[TaskInstantiationOutFull]


class PhaseOutFull(PhaseOut):
    objectives: List[ObjectiveOutFull]


class PhaseInstantiationOutFull(PhaseInstantiationOut):
    objectiveinstantiations: List[ObjectiveInstantiationOutFull]


class CoproductionSchemaOutFull(CoproductionSchemaOut):
    phases: List[PhaseOutFull]

class CoproductionProcessOutFull(CoproductionProcessOut):
    pass

class RoleOutFull(RoleOut):
    pass
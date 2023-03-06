import uuid

from app.treeitems.schemas import *


class ObjectiveCreate(TreeItemCreate):
    phase_id: Optional[uuid.UUID]
    disabler_id: Optional[str]
    disabled_on: Optional[datetime]


class ObjectivePatch(TreeItemPatch):
    pass


class Objective(ObjectiveCreate, TreeItem):
    class Config:
        orm_mode = True


class ObjectiveOut(Objective, TreeItemOut):
    pass

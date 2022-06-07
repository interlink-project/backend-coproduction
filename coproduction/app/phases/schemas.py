import uuid

from app.treeitems.schemas import *


class PhaseCreate(TreeItemCreate):
    coproductionprocess_id: Optional[uuid.UUID]


class PhasePatch(TreeItemPatch):
    pass


class Phase(PhaseCreate, TreeItem):
    class Config:
        orm_mode = True


class PhaseOut(Phase, TreeItemOut):
    pass

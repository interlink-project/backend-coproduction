import uuid

from app.treeitems.schemas import *


class PhaseCreate(TreeItemCreate):
    coproductionprocess_id: Optional[uuid.UUID]
    is_part_of_codelivery: Optional[bool]
    disabler_id: Optional[str]
    disabled_on: Optional[datetime]

class PhasePatch(TreeItemPatch):
    is_part_of_codelivery: Optional[bool]


class Phase(PhaseCreate, TreeItem):
    class Config:
        orm_mode = True


class PhaseOut(Phase, TreeItemOut):
    pass

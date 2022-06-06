from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Phase
from app.schemas import (
    PhaseCreate,
    PhasePatch,
)
import uuid
from app.utils import recursive_check

class CRUDPhase(CRUDBase[Phase, PhaseCreate, PhasePatch]):
    async def create_from_metadata(self, db: Session, phasemetadata: dict, coproductionprocess_id: uuid.UUID) -> Optional[Phase]:
        creator = PhaseCreate(**phasemetadata, coproductionprocess_id=coproductionprocess_id)
        return await self.create(db=db, phase=creator, commit=False)

    async def get_by_name(self, db: Session, name: str) -> Optional[Phase]:
        return db.query(Phase).filter(Phase.name == name).first()

    async def create(self, db: Session, *, phase: PhaseCreate, commit : bool = True) -> Phase:
        db_obj = Phase(
            name=phase.name,
            description=phase.description,
            # relations
            coproductionprocess_id=phase.coproductionprocess_id,
        )
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
            await self.log_on_create(db_obj)
        return db_obj

    async def add_prerequisite(self, db: Session, phase: Phase, prerequisite: Phase, commit : bool = True) -> Phase:
        if phase == prerequisite:
            raise Exception("Same object")

        recursive_check(phase.id, prerequisite)
        phase.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(phase)
        return phase

    # Override log methods
    def enrich_log_data(self, obj, logData):
        logData["model"] = "PHASE"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.coproductionprocess_id
        logData["phase_id"] = obj.id
        return logData


    # CRUD Permissions
    def can_create(self, user):
        return True

    def can_list(self, user):
        return True

    def can_read(self, user, object):
        return True

    def can_update(self, user, object):
        return True

    def can_remove(self, user, object):
        return True
    

exportCrud = CRUDPhase(Phase, logByDefault=True)

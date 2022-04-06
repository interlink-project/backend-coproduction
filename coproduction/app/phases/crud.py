from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Phase
from app.schemas import (
    PhaseCreate,
    PhasePatch,
)
import uuid

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
        return db_obj

    async def add_prerequisite(self, db: Session, phase: Phase, prerequisite: Phase, commit : bool = True) -> Phase:
        if phase == prerequisite:
            raise Exception("Same object")
        phase.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(phase)
        return phase

    async def remove(self, db: Session, *, id: uuid.UUID) -> Phase:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        related = db.query(Phase).filter(Phase.prerequisites.any(Phase.id == obj.id)).all()
        for i in related:
            i.prerequisites.remove(obj)
        db.delete(obj)
        db.commit()
        return obj

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


exportCrud = CRUDPhase(Phase)

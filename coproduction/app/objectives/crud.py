from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Objective, Phase
from app.schemas import (
    ObjectiveCreate,
    ObjectivePatch
)
import uuid
from app.utils import recursive_check

class CRUDObjective(CRUDBase[Objective, ObjectiveCreate, ObjectivePatch]):
    async def create_from_metadata(self, db: Session, objectivemetadata: dict, phase: Phase) -> Optional[Objective]:
        creator = ObjectiveCreate(**objectivemetadata)
        return await self.create(db=db, objective=creator, phase=phase, commit=False)

    async def get_by_name(self, db: Session, name: str) -> Optional[Objective]:
        if res := db.query(Objective).filter(Objective.name == name).first():
            await self.log_on_get(res)
            return res
        return

    async def create(self, db: Session, *, objective: ObjectiveCreate, phase: Phase = None, commit : bool = True) -> Objective:
        if phase and objective.phase_id:
            raise Exception("Specify only one objective")
        if not phase and not objective.phase_id:
            raise Exception("Objective not specified")

        db_obj = Objective(
            name=objective.name,
            description=objective.description,
            phase=phase,
            phase_id=objective.phase_id,
        )
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
            await self.log_on_create(db_obj)
        return db_obj

    async def add_prerequisite(self, db: Session, objective: Objective, prerequisite: Objective, commit : bool = True) -> Objective:
        if objective == prerequisite:
            raise Exception("Same object")
        # TODO: if objective in prerequisite.prerequisites => block

        recursive_check(objective.id, prerequisite)
        objective.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(objective)
        return objective

    # Override log methods
    def enrich_log_data(self, obj, logData):
        logData["model"] = "OBJECTIVE"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.phase.coproductionprocess_id
        logData["phase_id"] = obj.phase_id
        logData["objective_id"] = obj.id
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


exportCrud = CRUDObjective(Objective, logByDefault=True)

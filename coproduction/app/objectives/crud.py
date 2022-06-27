import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.messages import log
from app.models import Objective, Phase, User
from app.schemas import ObjectiveCreate, ObjectivePatch
from app.treeitems.crud import exportCrud as treeitems_crud
from app.utils import recursive_check
from fastapi.encoders import jsonable_encoder



class CRUDObjective(CRUDBase[Objective, ObjectiveCreate, ObjectivePatch]):
    async def create_from_metadata(self, db: Session, objectivemetadata: dict, phase: Phase, schema_id: uuid.UUID) -> Optional[Objective]:
        objectivemetadata["from_schema"] = schema_id
        objectivemetadata["from_item"] = objectivemetadata.get("id")
        creator = ObjectiveCreate(**objectivemetadata)
        return await self.create(db=db, obj_in=creator, commit=False, extra={
            "phase": phase
        })

    async def add_prerequisite(self, db: Session, objective: Objective, prerequisite: Objective, commit: bool = True) -> Objective:
        if objective == prerequisite:
            print(objective, prerequisite)
            raise Exception("Same object")
        # TODO: if objective in prerequisite.prerequisites => block

        recursive_check(objective.id, prerequisite)
        objective.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(objective)
        return objective

    async def remove(self, db: Session, *, id: uuid.UUID, user_id: str = None, remove_definitely: bool = False) -> Phase:
        obj = db.query(self.model).get(id)
        if not obj:
            raise Exception("Object does not exist")
        if remove_definitely:
            await self.log_on_remove(obj)
        else:
            await self.log_on_disable(obj)
        await treeitems_crud.remove(db=db, obj=obj, model=self.model, user_id=user_id, remove_definitely=remove_definitely)

    async def log_on_disable(self, obj):
        enriched: dict = self.enrich_log_data(obj, {
            "action": "DISABLE"
        })
        await log(enriched)

    # Override log methods
    def enrich_log_data(self, obj, logData):
        logData["model"] = "OBJECTIVE"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.phase.coproductionprocess_id
        logData["phase_id"] = obj.phase_id
        logData["objective_id"] = obj.id
        logData["roles"] = obj.user_roles
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

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.messages import log
from app.models import CoproductionProcess, Phase, User
from app.schemas import PhaseCreate, PhasePatch
from app.treeitems.crud import exportCrud as treeitems_crud
from app.utils import recursive_check
from fastapi.encoders import jsonable_encoder


class CRUDPhase(CRUDBase[Phase, PhaseCreate, PhasePatch]):
    async def create_from_metadata(self, db: Session, phasemetadata: dict, coproductionprocess: CoproductionProcess, schema_id: uuid.UUID) -> Optional[Phase]:
        data = phasemetadata.copy()
        del data["prerequisites_ids"]
        data["from_schema"] = schema_id
        data["from_item"] = data.get("id")
        creator = PhaseCreate(**data)
        return await self.create(db=db, obj_in=creator, commit=False, extra={
            "coproductionprocess": coproductionprocess
        })
        
    async def create(self, db: Session, *, obj_in: PhaseCreate, creator: User = None, extra: dict = {}, commit: bool = True) -> Phase:
        obj_in_data = jsonable_encoder(obj_in)
        prereqs = obj_in_data.get("prerequisites_ids")
        del obj_in_data["prerequisites_ids"]
        postreqs = obj_in_data.get("postrequisites_ids")
        del obj_in_data["postrequisites_ids"]

        db_obj = self.model(**obj_in_data, **extra)  # type: ignore

        if creator:
            db_obj.creator_id = creator.id
        
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
            await self.log_on_create(db_obj)
            
        if prereqs:
            for id in prereqs:
                phase = await self.get(db=db, id=id)
                if phase:
                   await self.add_prerequisite(db=db, phase=db_obj, prerequisite=phase)
        if postreqs:
            for id in postreqs:
                phase = await self.get(db=db, id=id)
                if phase:
                   await self.add_prerequisite(db=db, phase=phase, prerequisite=db_obj, commit=False)
                   
        if commit:
            db.commit()
            db.refresh(db_obj)

        return db_obj
            
    async def add_prerequisite(self, db: Session, phase: Phase, prerequisite: Phase, commit: bool = True) -> Phase:
        if phase == prerequisite:
            print(phase, prerequisite)
            raise Exception("Same object")

        recursive_check(phase.id, prerequisite)
        phase.prerequisites.clear()
        phase.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(phase)
        return phase

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
        logData["model"] = "PHASE"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.coproductionprocess_id
        logData["phase_id"] = obj.id
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


exportCrud = CRUDPhase(Phase, logByDefault=True)

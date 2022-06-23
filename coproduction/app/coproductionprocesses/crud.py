import uuid
from typing import List, Optional

from slugify import slugify
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app import crud, models
from app.general.utils.CRUDBase import CRUDBase
from app.models import CoproductionProcess, Permission, User, Permission
from app.permissions.crud import exportCrud as exportPermissionCrud
from app.schemas import CoproductionProcessCreate, CoproductionProcessPatch
from fastapi.encoders import jsonable_encoder
from app.messages import log


class CRUDCoproductionProcess(CRUDBase[CoproductionProcess, CoproductionProcessCreate, CoproductionProcessPatch]):
    async def get_multi_by_user(self, db: Session, user: User, search: str = None) -> Optional[List[CoproductionProcess]]:
        # await log({
        #     "model": self.modelName,
        #     "action": "LIST",
        # })
        admins = db.query(
            CoproductionProcess
        ).join(
            CoproductionProcess.administrators
        ).filter(
            User.id.in_([user.id])
        )

        user_permissions = db.query(
            CoproductionProcess
        ).join(
            CoproductionProcess.permissions
        ).filter(
            or_(
                Permission.user_id == user.id,
                Permission.team_id.in_(user.teams_ids)
            )
        )

        query = admins.union(user_permissions)
        if search:
            query = query.filter(
                CoproductionProcess.name.contains(search),
            )

        return query.all()

    async def clear_schema(self, db: Session, coproductionprocess: models.CoproductionProcess):
        schema = coproductionprocess.schema_used
        for phase in coproductionprocess.children:
            await crud.phase.remove(db=db, id=phase.id, remove_definitely=True)
        enriched: dict = self.enrich_log_data(coproductionprocess, {
            "action": "CLEAR_SCHEMA",
            "coproductionprocess_id": coproductionprocess.id,
            "coproductionschema_id": schema
        })
        await log(enriched)
        db.refresh(coproductionprocess)
        return coproductionprocess

    async def set_schema(self, db: Session, coproductionprocess: models.CoproductionProcess, coproductionschema: dict):
        total = {}
        schema_id = coproductionschema.get("id")
        for phasemetadata in coproductionschema.get("children", []):
            phasemetadata: dict
            db_phase = await crud.phase.create_from_metadata(
                db=db,
                phasemetadata=phasemetadata,
                coproductionprocess=coproductionprocess,
                schema_id=schema_id
            )

            #  Add new phase object and the prerequisites for later loop
            total[phasemetadata["id"]] = {
                "type": "phase",
                "prerequisites_ids": phasemetadata["prerequisites_ids"] or [],
                "newObj": db_phase,
            }

            for objectivemetadata in phasemetadata.get("children", []):
                objectivemetadata: dict
                db_obj = await crud.objective.create_from_metadata(
                    db=db,
                    objectivemetadata=objectivemetadata,
                    phase=db_phase,
                    schema_id=schema_id
                )
                #  Add new objective object and the prerequisites for later loop
                total[objectivemetadata["id"]] = {
                    "type": "objective",
                    "prerequisites_ids": objectivemetadata["prerequisites_ids"] or [],
                    "newObj": db_obj,
                }
                for taskmetadata in objectivemetadata.get("children", []):
                    db_task = await crud.task.create_from_metadata(
                        db=db,
                        taskmetadata=taskmetadata,
                        objective=db_obj,
                        schema_id=schema_id
                    )
                    total[taskmetadata["id"]] = {
                        "type": "task",
                        "prerequisites_ids": taskmetadata["prerequisites_ids"] or [],
                        "newObj": db_task,
                    }
        db.commit()

        for key, element in total.items():
            for pre_id in element["prerequisites_ids"]:

                if element["type"] == "phase":
                    await crud.phase.add_prerequisite(db=db, phase=element["newObj"], prerequisite=total[pre_id]["newObj"], commit=False)
                if element["type"] == "objective":
                    await crud.objective.add_prerequisite(db=db, objective=element["newObj"], prerequisite=total[pre_id]["newObj"], commit=False)
                if element["type"] == "task":
                    await crud.task.add_prerequisite(db=db, task=element["newObj"], prerequisite=total[pre_id]["newObj"], commit=False)

        schema_id = coproductionschema.get("id")
        coproductionprocess.schema_used = schema_id
        db.commit()
        enriched: dict = self.enrich_log_data(coproductionprocess, {
            "action": "SET_SCHEMA",
            "coproductionprocess_id": coproductionprocess.id,
            "coproductionschema_id": schema_id
        })
        await log(enriched)
        db.refresh(coproductionprocess)
        return coproductionprocess

    # Override log methods
    def enrich_log_data(self, coproductionprocess, logData):
        logData["model"] = "COPRODUCTIONPROCESS"
        logData["object_id"] = coproductionprocess.id
        logData["coproductionprocess_id"] = coproductionprocess.id
        return logData

    # CRUD Permissions
    def can_create(self, user):
        return True

    def can_list(self, user):
        return True

    def check_perm(self, db: Session, user: models.User, object, perm):
        return True

    def can_read(self, db: Session, user, object):
        first = db.query(CoproductionProcess).filter(
            CoproductionProcess.id == object.id
        ).filter(
            CoproductionProcess.id == Permission.coproductionprocess_id
        ).filter(
            or_(
                Permission.user_id == user.id,
                Permission.team_id.in_(user.teams_ids)
            )
        )
        second = db.query(CoproductionProcess).filter(
            CoproductionProcess.id == object.id
        ).filter(
            CoproductionProcess.administrators.any(models.User.id.in_([user.id]))
        )
        return len(second.union(first).all()) > 0

    def can_update(self, user, object):
        return user in object.administrators

    def can_remove(self, user, object):
        return user in object.administrators


exportCrud = CRUDCoproductionProcess(CoproductionProcess, logByDefault=True)

import uuid
from typing import List, Optional

from slugify import slugify
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import crud, models
from app.general.utils.CRUDBase import CRUDBase
from app.models import CoproductionProcess, Permission, User, Permission
from app.permissions.crud import exportCrud as exportPermissionCrud
from app.schemas import CoproductionProcessCreate, CoproductionProcessPatch
from fastapi.encoders import jsonable_encoder


class CRUDCoproductionProcess(CRUDBase[CoproductionProcess, CoproductionProcessCreate, CoproductionProcessPatch]):
    async def get_by_name(self, db: Session, name: str) -> Optional[CoproductionProcess]:
        # await log({
        #     "model": self.modelName,
        #     "action": "GET_BY_NAME",
        #     "crud": True,
        #     "name": name
        # })
        return db.query(CoproductionProcess).filter(CoproductionProcess.name == name).first()

    async def get_multi_by_user(self, db: Session, user: User) -> Optional[List[CoproductionProcess]]:
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
        return admins.union(user_permissions).all()

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

        coproductionprocess.schema_used = coproductionschema.get("id")
        db.commit()
        # await log({
        #     "model": self.modelName,
        #     "action": "SET_SCHEMA",
        #     "crud": True,
        #     "coproductionprocess_id": db_obj.id,
        #     "coproductionschema_id": coproductionschema.get("id", None)
        # })
        db.refresh(coproductionprocess)
        return coproductionprocess

    async def add_team(self, db: Session, coproductionprocess: models.CoproductionProcess, team: models.Team):
        if obj := await exportPermissionCrud.add_team(db=db, permission=coproductionprocess.default_permission, team=team):
            # await log({
            #     "model": self.modelName,
            #     "action": "ADD_TEAM",
            #     "coproductionprocess_id": obj.id,
            #     "team_id": team.id
            # })
            return obj
        return

    async def add_user(self, db: Session, coproductionprocess: models.CoproductionProcess, user: models.User):
        if obj := await exportPermissionCrud.add_user(db=db, permission=coproductionprocess.default_permission, user=user):
            # await log({
            #     "model": self.modelName,
            #     "action": "ADD_USER",
            #     "crud": True,
            #     "coproductionprocess_id": obj.id,
            #     "user_id": user.id
            # })
            return obj
        return

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

    def can_update(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="update")

    def can_remove(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="delete")


exportCrud = CRUDCoproductionProcess(CoproductionProcess, logByDefault=True)

import uuid
from typing import List, Optional

from slugify import slugify
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app import crud, models
from app.general.utils.CRUDBase import CRUDBase
from app.models import CoproductionProcess, Permission, User, Permission, TreeItem, Asset
from app.schemas import CoproductionProcessCreate, CoproductionProcessPatch, PermissionCreate
from fastapi.encoders import jsonable_encoder
from app.messages import log
from app.treeitems.crud import exportCrud as treeitemsCrud
from app.sockets import socket_manager

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
            ),
        )

        query = admins.union(user_permissions)
        if search:
            query = query.filter(
                CoproductionProcess.name.contains(search),
            )

        return query.order_by(CoproductionProcess.created_at.asc()).all()


    async def get_assets(self, db: Session, coproductionprocess: CoproductionProcess, user: models.User):
        # print(self.can_read(db, user, coproductionprocess))
        if user in coproductionprocess.administrators: #or self.can_read(db, user, coproductionprocess):
            return db.query(
                Asset
                ).filter(
                    Asset.task_id.in_(coproductionprocess.task_ids())
                ).order_by(models.Asset.created_at.desc()).all()
                
        ids = [treeitem.id for treeitem in await treeitemsCrud.get_for_user_and_coproductionprocess(db=db, user=user, coproductionprocess_id=coproductionprocess.id) if not treeitem.disabled_on]
        
        listOfAssets= db.query(
                models.Asset
            ).filter(
                or_(
                    models.Asset.phase_id.in_(ids),
                    models.Asset.objective_id.in_(ids),
                    models.Asset.task_id.in_(ids),
                )
            ).order_by(models.Asset.created_at.desc()).all()
        
        #Check if the user has the permissions to see the asset.
        for asset in listOfAssets:
            print(asset)
            tienePermisosListado=crud.asset.can_list(db=db,user=user,task=asset.task)
            if not tienePermisosListado:
                listOfAssets.remove(asset)
        
        return listOfAssets

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
        await socket_manager.send_to_id(coproductionprocess.id, {"event": "schema_cleared"})
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
        await socket_manager.send_to_id(coproductionprocess.id, {"event": "schema_set"})
        return coproductionprocess
    
    async def copy(self, db: Session, coproductionprocess: CoproductionProcessCreate, user: models.User, token):
        print(coproductionprocess.logotype)
        new_coproductionprocess = CoproductionProcessCreate(
            schema_used=coproductionprocess.schema_used,
            language=coproductionprocess.language,
            name="Copy of " + coproductionprocess.name,
            description=coproductionprocess.description,
            logotype=coproductionprocess.logotype,
            aim=coproductionprocess.aim,
            idea=coproductionprocess.idea,
            organization_desc=coproductionprocess.organization,
            challenges=coproductionprocess.challenges,
            status=coproductionprocess.status,
        )
        
        db_obj = await self.create(db=db, obj_in=new_coproductionprocess, creator=user, set_creator_admin=True)

        administrators = coproductionprocess.administrators
        for admin in administrators:
            await self.add_administrator(db=db, db_obj=db_obj, user=admin)

        phases_temp = coproductionprocess.children.copy()
        phases = []
        for id, phase in enumerate(phases_temp):
            if not phase.prerequisites_ids:
                phases.append(phase)
                phases_temp.pop(id)

        while phases_temp:
            for id, phase in enumerate(phases_temp):
                if str(phase.prerequisites_ids[0]) == str(phases[-1].id):
                    phases.append(phase)
                    phases_temp.pop(id)

        #  Create a dict with the old ids and the new ids
        ids_dict = {}
        for phase in phases:
            tmp_phase, phase_id_updates = await crud.phase.copy(db=db, obj_in=phase, coproductionprocess=db_obj, extra=ids_dict)
            ids_dict['Phase_'+str(phase.id)] = tmp_phase.id
            ids_dict.update(phase_id_updates)

        # Copy the assets of the project
        assets = await self.get_assets(db, coproductionprocess, user)
        for asset in assets:
            task = await crud.task.get(db, ids_dict['Task_' + str(asset.task_id)])
            await crud.asset.copy(db, asset, user, task, token)

        # Copy the permissions of the project (THE NEW CREATOR IS THE CREATOR OF THE COPY)
        for permission in coproductionprocess.permissions:
            treeitem = None
            if permission.treeitem:
                treeitem = await treeitemsCrud.get(db, ids_dict[permission.treeitem.__class__.__name__ + '_' + str(permission.treeitem.id)])

            new_permission = PermissionCreate(
                creator_id=user.id,
                creator=user,
                team_id=permission.team_id,
                team=permission.team,
                coproductionprocess_id=db_obj.id if permission.coproductionprocess else None,
                coproductionprocess=db_obj if permission.coproductionprocess else None,
                treeitem_id=treeitem.id if treeitem else None,
                treeitem=treeitem,
                access_assets_permission=permission.access_assets_permission,
                create_assets_permission=permission.create_assets_permission,
                delete_assets_permission=permission.delete_assets_permission)

            await crud.permission.create(db=db, obj_in=new_permission, creator=user)

        return db_obj


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

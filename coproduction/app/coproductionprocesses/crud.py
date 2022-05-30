from multiprocessing.dummy import Value
import uuid
from typing import List, Optional

from slugify import slugify
from sqlalchemy.orm import Session

from app import crud, models
from app.general.utils.CRUDBase import CRUDBase
from app.models import CoproductionProcess, Team, Role, User
from app.roles.crud import exportCrud as exportRoleCrud
from app.roles.models import AdministratorRole, DefaultRole, UnauthenticatedRole
from app.schemas import CoproductionProcessCreate, CoproductionProcessPatch, TreeItemCreate
from sqlalchemy import or_
from app.messages import log

class CRUDCoproductionProcess(CRUDBase[CoproductionProcess, CoproductionProcessCreate, CoproductionProcessPatch]):
    async def get_by_name(self, db: Session, name: str) -> Optional[Team]:
        # await log({
        #     "model": self.modelName,
        #     "action": "GET_BY_NAME",
        #     "crud": True,
        #     "name": name
        # })
        return db.query(CoproductionProcess).filter(CoproductionProcess.name == name).first()

    async def get_multi_by_user(self, db: Session, user: User) -> Optional[List[CoproductionProcess]]:
        team_ids = user.team_ids
        # await log({
        #     "model": self.modelName,
        #     "action": "LIST",
        # })
        return db.query(
            CoproductionProcess
        ).join(
            CoproductionProcess.roles
        ).filter(
            or_(
                Role.users.any(User.id.in_([user.id])),
                Role.teams.any(Team.id.in_(team_ids))
            )
        ).all()

    async def create(self, db: Session, *, coproductionprocess: CoproductionProcessCreate, creator: models.User, team: models.Team) -> CoproductionProcess:
        db_obj = CoproductionProcess(
            # uses postgres
            name=coproductionprocess.name,
            description=coproductionprocess.description,
            language=coproductionprocess.language,
            aim=coproductionprocess.aim,
            idea=coproductionprocess.idea,
            organization=coproductionprocess.organization,
            challenges=coproductionprocess.challenges,
            # relations
            creator=creator,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Add mandatory roles
        data = AdministratorRole.dict()
        admin_role = models.Role(**data, coproductionprocess=db_obj, perms_editable=False,
                                 meta_editable=False, deletable=False, selectable=True)
        db.add(admin_role)

        data = UnauthenticatedRole.dict()
        db_role = models.Role(**data, coproductionprocess=db_obj, perms_editable=True,
                              meta_editable=False, deletable=False, selectable=False)
        db.add(db_role)

        data = DefaultRole.dict()
        default_role = models.Role(**data, coproductionprocess=db_obj, perms_editable=True,
                                   meta_editable=False, deletable=False, selectable=True)
        db.add(default_role)

        # Set the main team as admin
        await exportRoleCrud.add_user(db=db, role=admin_role, user=creator)
        if team:
            await exportRoleCrud.add_team(db=db, role=admin_role, team=team)

        db_obj.default_role = default_role
        db.commit()
        # await log({
        #     "model": self.modelName,
        #     "action": "CREATE",
        #     "crud": True,
        #     "coproductionprocess_id": db_obj.id,
        # })
        db.refresh(db_obj)
        return db_obj

    async def create_recursive(self, db, data, extra_add):
        resume = {}
        children = data.get("children", [])
        del data["children"]
        db_treeitem = await crud.treeitem.create(
                db=db,
                treeitem=TreeItemCreate(**{
                    **data, 
                    **extra_add,                
                }),
            )
        resume = {
            data["id"]: {
                "prerequisites_ids": data["prerequisites_ids"] or [],
                "newObj": db_treeitem,
            }
        }

        
        for child in children:
            child_ret = await self.create_recursive(db=db, data=child, extra_add={
                "parent_id": db_treeitem.id
            })
            resume = {**resume, **child_ret}
        return resume
            

    async def set_schema(self, db: Session, coproductionprocess: models.CoproductionProcess, coproductionschema: dict):
        treeitems = coproductionschema.get("treeitems", [])

        resume = {}
        for treeitem in treeitems:
            print("PROCESSING", treeitem.get("name"))
            child_ret = await self.create_recursive(db=db, data=treeitem, extra_add={
                "coproductionprocess_id": coproductionprocess.id
            })
            resume = {**resume, **child_ret}

        print("RESUMEEE", resume)
        db.commit()

        for key, element in resume.items():
            for pre_id in element["prerequisites_ids"]:
                await crud.treeitem.add_prerequisite(db=db, treeitem=element["newObj"], prerequisite=resume[pre_id]["newObj"], commit=False)
        db.commit()
        
        db.refresh(coproductionprocess)
        return coproductionprocess

    async def add_team(self, db: Session, coproductionprocess: models.CoproductionProcess, team: models.Team):
        if obj := await exportRoleCrud.add_team(db=db, role=coproductionprocess.default_role, team=team):
            # await log({
            #     "model": self.modelName,
            #     "action": "ADD_TEAM",
            #     "coproductionprocess_id": obj.id,
            #     "team_id": team.id
            # })
            return obj
        return

    async def add_user(self, db: Session, coproductionprocess: models.CoproductionProcess, user: models.User):
        if obj := await exportRoleCrud.add_user(db=db, role=coproductionprocess.default_role, user=user):
            # await log({
            #     "model": self.modelName,
            #     "action": "ADD_USER",
            #     "crud": True,
            #     "coproductionprocess_id": obj.id,
            #     "user_id": user.id
            # })
            return obj
        return

    # CRUD Permissions
    def can_create(self, user):
        return True

    def can_list(self, user):
        return True

    def check_perm(self, db: Session, user: models.User, object, perm):
        return True

    def can_read(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="retrieve")

    def can_update(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="update")

    def can_remove(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="delete")


exportCrud = CRUDCoproductionProcess(CoproductionProcess)

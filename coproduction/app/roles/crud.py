from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app import models, schemas
from app.general.utils.CRUDBase import CRUDBase
from app.models import Role, User, Team
from app.messages import log

class CRUDRole(CRUDBase[Role, schemas.RoleCreate, schemas.RolePatch]):
    async def get_roles_of_user_for_coproductionprocess(self, db: Session, coproductionprocess: models.CoproductionProcess, user: models.User) -> Role:
        # predominan los individuales
        if individual_role := db.query(Role).filter(
                Role.coproductionprocess_id == coproductionprocess.id
            ).filter(
                Role.users.any(User.id.in_([user.id]))
            ).first():
            return [individual_role]

        return db.query(Role).filter(
                Role.coproductionprocess_id == coproductionprocess.id
            ).filter(
                Role.teams.any(Team.id.in_(user.team_ids))
            ).all()
    
    async def get_permissions_of_user_for_coproductionprocess(self, db: Session, coproductionprocess: models.CoproductionProcess, user: models.User) -> Role:
        perms = []
        role: Role
        for role in await self.get_roles_of_user_for_coproductionprocess(db=db, coproductionprocess=coproductionprocess, user=user):
            perms += role.permissions
        return perms

    async def check_permission_on_coproductionprocess(self, db: Session, permission: str, coproductionprocess: models.CoproductionProcess, user: models.User) -> Role:
        return permission in await self.get_permissions_of_user_for_coproductionprocess(db=db, coproductionprocess=coproductionprocess, user=user)

    async def add_team(self, db: Session, role: Role, team: models.Team):
        role.teams.append(team)
        db.commit()
        db.refresh(role)
        await log(self.enrich_log_data(role, {"action": "ADD_TEAM", "added_team_id": team.id}))   
        return role
    
    async def add_user(self, db: Session, role: Role, user: models.User):
        role.users.append(user)
        db.commit()
        db.refresh(role)
        await log(self.enrich_log_data(role, {"action": "ADD_USER", "added_user_id": user.id}))
        return role
    
    async def remove_team(self, db: Session, role: Role, team: models.Team):
        role.teams.remove(team)
        db.commit()
        db.refresh(role)
        await log(self.enrich_log_data(role, {"action": "REMOVE_TEAM", "removed_team_id": team.id}))
        return role
    
    async def remove_user(self, db: Session, role: Role, user: models.User):
        role.users.remove(user)
        db.commit()
        db.refresh(role)
        await log(self.enrich_log_data(role, {"action": "REMOVE_USER", "removed_user_id": user.id}))
        return role

    def enrich_log_data(self, obj, logData):
        logData["model"] = "ROLE"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.coproductionprocess_id
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
        if not object.deletable:
            return False
        return True

exportCrud = CRUDRole(Role, logByDefault=True)

from typing import Optional
from sqlalchemy.orm import Session

from app import models, schemas
from app.general.utils.CRUDBase import CRUDBase
from app.roles.models import Role

class CRUDRole(CRUDBase[Role, schemas.RoleCreate, schemas.RolePatch]):
    def create(self, db: Session, role: schemas.RoleCreate) -> Role:
        db_role = models.Role(**role.dict())
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role

    def add_team(self, db: Session, role: Role, team: models.Team):
        role.teams.append(team)
        db.commit()
        db.refresh(role)
        return role
    
    def add_user(self, db: Session, role: Role, user: models.User):
        role.users.append(user)
        db.commit()
        db.refresh(role)
        return role
    
    def remove_team(self, db: Session, role: Role, team: models.Team):
        role.teams.remove(team)
        db.commit()
        db.refresh(role)
        return role
    
    def remove_user(self, db: Session, role: Role, user: models.User):
        role.users.remove(user)
        db.commit()
        db.refresh(role)
        return role

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

exportCrud = CRUDRole(Role)

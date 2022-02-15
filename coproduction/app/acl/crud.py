from email.policy import default
from sqlalchemy.orm import Session
from typing import List
from app.models import ACL
from app.schemas import ACLCreate, ACLPatch
from app.general.utils.CRUDBase import CRUDBase
from app import models, schemas
import uuid
from app.acl.models import Role, AdministratorRole, UnauthenticatedRole
from app.coproductionprocesses.crud import exportCrud as coroductionprocesses_crud

class CRUDACL(CRUDBase[ACL, ACLCreate, ACLPatch]):
    def create(self, db: Session, acl: ACLCreate) -> ACL:
        db_acl = ACL(
            coproductionprocess_id=acl.coproductionprocess_id,
        )
        
        db.add(db_acl)
        db.commit()

        # Add default roles
        data = AdministratorRole.dict()
        data["acl_id"] = db_acl.id
        admin_role = models.Role(**data, perms_editable=False, meta_editable=False, deletable=False, selectable=True)
        db.add(admin_role)
        
        # Set the main membership as admin
        data = UnauthenticatedRole.dict()
        data["acl_id"] = db_acl.id
        db_role = models.Role(**data, perms_editable=True, meta_editable=False, deletable=False, selectable=False)
        db.add(db_role)
         
        cp = coroductionprocesses_crud.get(db=db, id=acl.coproductionprocess_id)
        exportRoleCrud.set_role_to_team(db=db, role=admin_role, team=cp.team)

        db.commit()
        db.refresh(db_acl)
        return db_acl
        
    def remove(self, db: Session, *, id: uuid.UUID) -> ACL:
        obj = db.query(ACL).get(id)
        db.delete(obj)
        db.commit()
        # TODO: remove from external microservice
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

exportCrud = CRUDACL(ACL)


class CRUDRole(CRUDBase[Role, schemas.RoleCreate, schemas.RolePatch]):
    
    def create(self, db: Session, role: schemas.RoleCreate) -> Role:
        db_role = models.Role(**role.dict())
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    def set_role_to_team(self, db: Session, team: models.Team, role: Role):
        for membership in team.memberships:
            role.memberships.append(membership)
        db.commit()
        db.refresh(team)
        return team

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
        if not object.editable:
            return False
        return True

exportRoleCrud = CRUDRole(Role)
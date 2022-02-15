from email.policy import default
from sqlalchemy.orm import Session
from typing import List
from app.models import ACL
from app.schemas import ACLCreate, ACLPatch
from app.general.utils.CRUDBase import CRUDBase
from app import models, schemas
import uuid
from app.acl.models import Role, AdministratorRole, UnauthenticatedRole, DefaultRole
from app.coproductionprocesses.crud import exportCrud as coroductionprocesses_crud

class CRUDACL(CRUDBase[ACL, ACLCreate, ACLPatch]):
    def create(self, db: Session, coproductionprocess: models.CoproductionProcess) -> ACL:
        db_acl = ACL(
            coproductionprocess_id=coproductionprocess.id,
        )
        db.add(db_acl)

        # Add mandatory roles
        data = AdministratorRole.dict()
        admin_role = models.Role(**data, acl=db_acl, perms_editable=False, meta_editable=False, deletable=False, selectable=True)
        db.add(admin_role)
        
        data = UnauthenticatedRole.dict()
        db_role = models.Role(**data, acl=db_acl, perms_editable=True, meta_editable=False, deletable=False, selectable=False)
        db.add(db_role)

        data = DefaultRole.dict()
        default_role = models.Role(**data, acl=db_acl, perms_editable=True, meta_editable=False, deletable=False, selectable=True)
        db.add(default_role)
        
        # Set the main team members as admin
        for membership in coproductionprocess.teams[0].memberships:
            admin_role.memberships.append(membership)

        db_acl.default_role = default_role
        db.commit()
        db.refresh(db_acl)
        return db_acl

    def check_action(self, db: Session, user: models.User, action: str) -> ACL:
        return True

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

exportRoleCrud = CRUDRole(Role)
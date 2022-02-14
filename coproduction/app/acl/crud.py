from email.policy import default
from sqlalchemy.orm import Session
from typing import List
from app.models import ACL
from app.schemas import ACLCreate, ACLPatch
from app.general.utils.CRUDBase import CRUDBase
from app import models, schemas
import uuid
from app.acl.models import get_default_roles, Role
from app.coproductionprocesses.crud import exportCrud as coroductionprocesses_crud

class CRUDACL(CRUDBase[ACL, ACLCreate, ACLPatch]):
    def create(self, db: Session, acl: ACLCreate) -> ACL:
        db_obj = ACL(
            coproductionprocess_id=acl.coproductionprocess_id,
        )
        
        db.add(db_obj)
        db.commit()

        # Add default roles
        roles = acl.roles or [schemas.RoleBase(**data) for data in get_default_roles()]
        role : schemas.RoleBase
        for role in roles:
            data = role.dict()
            data["acl_id"] = db_obj.id
            
            if role.name == "Unauthenticated":
                db_role = models.Role(**data, perms_editable=True, name_editable=False)
            # Set the main team as admin
            if role.name == "Administrator":
                db_role = models.Role(**data, perms_editable=False, name_editable=False)
                cp = coroductionprocesses_crud.get(db=db, id=acl.coproductionprocess_id)
                db_role.teams.append(cp.team)
            db.add(db_role)

        db.commit()
        db.refresh(db_obj)
        return db_obj
        
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
        return True

exportRoleCrud = CRUDRole(Role)
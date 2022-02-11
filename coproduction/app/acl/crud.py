from email.policy import default
from sqlalchemy.orm import Session
from typing import List
from app.models import ACL
from app.schemas import ACLCreate, ACLPatch
from app.general.utils.CRUDBase import CRUDBase
from app import models, schemas
import uuid
from app.acl.models import DEFAULT_ROLES

default_roles = [schemas.RoleBase(**data) for data in DEFAULT_ROLES]
print(default_roles)

class CRUDACL(CRUDBase[ACL, ACLCreate, ACLPatch]):
    def create(self, db: Session, acl: ACLCreate) -> ACL:
        db_obj = ACL(
            coproductionprocess_id=acl.coproductionprocess_id,
        )
        
        db.add(db_obj)
        db.commit()

        roles = acl.roles or default_roles
        role : schemas.RoleBase
        for role in roles:
            data = role.dict()
            data["acl_id"] = db_obj.id
            print(data)
            db_role = models.Role(**data)
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
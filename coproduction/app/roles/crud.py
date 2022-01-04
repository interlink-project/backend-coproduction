import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Role
from app.schemas import RoleCreate, RolePatch
from sqlalchemy import and_

class CRUDRole(CRUDBase[Role, RoleCreate, RolePatch]):
    def get_user_role_for_process(self, db: Session, user_id: str, coproductionprocess_id: uuid.UUID) -> Optional[Role]:
        return db.query(Role).filter(and_(Role.user_id == user_id, Role.coproductionprocess_id == coproductionprocess_id)).first()
    
    def get_all_user_roles(self, db: Session, user_id: str) -> Optional[Role]:
        return db.query(Role).filter(Role.user_id == user_id)

    def create(self, db: Session, role: RoleCreate) -> Role:
        db_obj = Role(
            role=role.role,
            type=role.type,
            coproductionprocess_id=role.coproductionprocess_id,
            user_id=role.user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

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


exportCrud = CRUDRole(Role)

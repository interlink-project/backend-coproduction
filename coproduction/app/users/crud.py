from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import User
from app.schemas import UserCreate, UserPatch

class CRUDUser(CRUDBase[User, UserCreate, UserPatch]):
    async def get(self, db: Session, id: str) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()
    
    async def get_multi_by_ids(self, db: Session, ids: list) -> Optional[User]:
        return db.query(User).filter(User.id.in_(ids)).all()

    async def create(self, db: Session, user: UserCreate) -> User:
        print(f"CREATING USER {user.id}")
        db_obj = User(
            id=user.id,
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


exportCrud = CRUDUser(User)

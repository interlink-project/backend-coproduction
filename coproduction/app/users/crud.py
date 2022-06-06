from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import User
from app.schemas import UserCreate, UserPatch

class CRUDUser(CRUDBase[User, UserCreate, UserPatch]):
    async def get_multi_by_ids(self, db: Session, ids: list) -> Optional[User]:
        return db.query(User).filter(User.id.in_(ids)).all()

    async def get_or_create(self, db: Session, data: dict) -> Optional[User]:
        if "sub" in data:
            data["id"] = data.get("sub")
            if user := await self.get(db=db, id=data.get("id")):
                return user
            else:
                return await self.create(db=db, obj_in=UserCreate(**data))
        raise Exception("Sub not in data")

    # Override log methods
    def enrich_log_data(self, obj, logData):
        logData["model"] = "USER"
        logData["object_id"] = obj.id
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
        return True


exportCrud = CRUDUser(User, logByDefault=True)

from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import User
from app.schemas import UserCreate, UserPatch
import uuid
from sqlalchemy import or_

class CRUDUser(CRUDBase[User, UserCreate, UserPatch]):
    async def get(self, db: Session, id: uuid.UUID) -> Optional[User]:
        if obj := db.query(User).filter(
            or_(
                User.id == id,
                User.email == id
            )
        ).first():
            await self.log_on_get(obj)
            return obj
        return

    async def get_multi_by_ids(self, db: Session, ids: list) -> List[User]:
        return db.query(User).filter(User.id.in_(ids)).all()

    async def get_or_create(self, db: Session, data: dict) -> Optional[User]:
        if "sub" in data:
            data["id"] = data.get("sub")
            if user := await self.get(db=db, id=data.get("id")):
                return await self.update(db=db, db_obj=user, obj_in=UserPatch(**data))
            
            # try with email
            if user := await self.get(db=db, id=data.get("email")):
                return await self.update(db=db, db_obj=user, obj_in=UserPatch(**data))
            else:
                return await self.create(db=db, obj_in=UserCreate(**data))
        raise Exception("Sub not in data")

    # Override log methods
    def enrich_log_data(self, obj, logData):
        logData["model"] = "USER"
        logData["object_id"] = obj.id
        return logData

    async def log_on_update(self, obj):
        return

    # CRUD Permissions
    def can_create(self, user):
        # user updated frequently => do not log
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

from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import User
from app.schemas import UserCreate, UserPatch
from sqlalchemy import or_
import requests
from app.config import settings
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

class CRUDUser(CRUDBase[User, UserCreate, UserPatch]):
    def get(self, db: Session, id: str) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_or_create(self, db: Session, token_data: dict):
        print(f"GET OR CREATING USER")
        if (user := self.get(db=db, id=token_data["sub"])):
            return user
        else:
            try:
                response = requests.post(f"http://{settings.AUTH_SERVICE}/auth/api/v1/users", json=token_data).json()
                return self.create(db=db, user=UserCreate(id=response["sub"]))
            except IntegrityError as e:
                assert isinstance(e.orig, UniqueViolation)
                return self.get(db=db, id=token_data["sub"])

    def create(self, db: Session, user: UserCreate) -> User:
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

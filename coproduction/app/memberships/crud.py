from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Membership
from app.schemas import MembershipCreate, MembershipPatch
from app.users.crud import exportCrud as users_crud
import uuid
from app import models

class CRUDMembership(CRUDBase[Membership, MembershipCreate, MembershipPatch]):
    def get_by_user_id(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> Optional[Membership]:
        return db.query(Membership).filter(Membership.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_by_team_id(self, db: Session, team_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Optional[Membership]:
        return db.query(Membership).filter(Membership.team_id == team_id).offset(skip).limit(limit).all()

    def create(self, db: Session, membership: MembershipCreate) -> Membership:     
        user = users_crud.get(db=db, id=membership.user_id)
        if not user:
            raise Exception("Could not retrieve user")
        db_obj = Membership(
            user_id=user.id,
            team_id=membership.team_id,
        )
        # TODO: send to coproduction to create ROLES
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # TODO: if removed, get all roles == admin and set to another user

    def can_create(self, membership):
        return True

    def can_list(self, membership):
        return True

    def can_read(self, membership, object):
        return True
    
    def can_update(self, membership, object):
        return True
    
    def can_remove(self, membership, object):
        return True

exportCrud = CRUDMembership(Membership)

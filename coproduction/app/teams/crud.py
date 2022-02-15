from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import Team
from app.schemas import TeamCreate, TeamPatch
import uuid
from app import models
from app.memberships.crud import exportCrud as memberships_crud
from app.acl.crud import exportRoleCrud as roles_crud
from app import schemas

class CRUDTeam(CRUDBase[Team, TeamCreate, TeamPatch]):
    def get_by_name(self, db: Session, name: str) -> Optional[Team]:
        return db.query(Team).filter(Team.name == name).first()

    def get_multi_by_user(self, db: Session, user_id: str) -> Optional[Team]:
        return db.query(
            Team,
        ).filter(
            Team.id == models.Membership.team_id,
        ).filter(
            models.Membership.user_id == models.User.id,
        ).filter(
            models.User.id == user_id,
        ).all()

    def create(self, db: Session, team: TeamCreate, creator: models.User) -> Team:
        db_obj = Team(
            name=team.name,
            description=team.description,
            creator=creator
        )
        db.add(db_obj)
        db.commit()

        for user_id in team.user_ids:
            memberships_crud.create(db=db, membership=schemas.MembershipCreate(team_id=db_obj.id, user_id=user_id))

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


exportCrud = CRUDTeam(Team)

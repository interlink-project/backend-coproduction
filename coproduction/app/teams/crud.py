from app.messages import log
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import Team
from app.schemas import TeamCreate, TeamPatch
import uuid
from app import models
from app.users.crud import exportCrud as users_crud

class CRUDTeam(CRUDBase[Team, TeamCreate, TeamPatch]):
    async def get_multi_filtered(
        self, db: Session
    ) -> List[Team]:
        queries = []
        return db.query(Team).filter(*queries).all()

    async def get_by_name(self, db: Session, name: str) -> Optional[Team]:
        return db.query(Team).filter(Team.name == name).first()

    async def get_multi_by_user(self, db: Session, user_id: str) -> Optional[List[Team]]:
        return db.query(
            Team,
        ).filter(Team.users.any(models.User.id.in_([user_id]))).all()

    async def add_user(self, db: Session, team: Team, user: models.User) -> Team:
        team.users.append(user)
        db.commit()
        db.refresh(team)
        await log(self.enrich_log_data(team, {
            "model": "TEAM",
            "action": "ADD_USER",
            "added_user_id": user.id
        }))
        return team

    async def remove_user(self, db: Session, team: Team, user: models.User) -> Team:
        if team.creator_id != user.id:
            team.users.remove(user)
            db.commit()
            db.refresh(team)
            await log(self.enrich_log_data(team, {
                "model": "TEAM",
                "action": "REMOVE_USER",
                "removed_user_id": user.id
            }))
            return team
        raise Exception("Can not remove team creator")
        
    async def create(self, db: Session, team: TeamCreate, creator: models.User) -> Team:
        db_obj = Team(
            name=team.name,
            description=team.description,
            creator=creator
        )
        for user in await users_crud.get_multi_by_ids(db=db, ids=team.user_ids):
            db_obj.users.append(user)

        db_obj.administrators.append(creator)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        await self.log_on_create(db_obj)
        return db_obj
    
    # Override log methods
    def enrich_log_data(self, obj, logData):
        logData["model"] = "TEAM"
        logData["object_id"] = obj.id
        logData["team_id"] = obj.id
        return logData

    # CRUD Permissions
    def can_create(self, user):
        return True

    def can_list(self, user):
        return True

    def can_read(self, user, object):
        return True

    def can_update(self, user, object):
        return user in object.administrators

    def can_remove(self, user, object):
        return user in object.administrators


exportCrud = CRUDTeam(Team)

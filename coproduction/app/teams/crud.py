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
        self, db: Session, coproductionprocess_id: uuid.UUID
    ) -> List[Team]:
        queries = []
        # if coproductionprocess_id:
        #     queries.append(Team.roles.any(models.Role.id.in_([coproductionprocess_id])))
        # else:
        #     queries.append(Team.is_public == False)
        return db.query(Team).filter(*queries).all()

    async def get_by_name(self, db: Session, name: str) -> Optional[Team]:
        return db.query(Team).filter(Team.name == name).first()

    async def get_multi_by_user(self, db: Session, user_id: str) -> Optional[List[Team]]:
        return db.query(
            Team,
        ).filter(Team.users.any(models.User.id.in_([user_id]))).all()
    
    # async def get_multi_by_process(self, db: Session, coproductionprocess_id: uuid.UUID) -> Optional[List[Team]]:
    #     return db.query(
    #         Team,
    #     ).filter(Team.roles.any(models.Role.id.in_([coproductionprocess_id]))).all()

    async def add_user(self, db: Session, team: Team, user: models.User) -> Team:
        team.users.append(user)
        db.commit()
        db.refresh(team)
        await log({
            "model": "TEAM",
            "action": "ADD_USER",
            "team_id": team.id,
            "added_user_id": user.id
        })
        return team
        
    async def create(self, db: Session, team: TeamCreate, creator: models.User) -> Team:
        db_obj = Team(
            name=team.name,
            description=team.description,
            creator=creator
        )
        db.add(db_obj)
        db.commit()

        for user in await users_crud.get_multi_by_ids(db=db, ids=team.user_ids):
            db_obj.users.append(user)
            
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


exportCrud = CRUDTeam(Team)

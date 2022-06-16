from app.messages import log
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import Team
from app.schemas import TeamCreate, TeamPatch
import uuid
from app import models
from app.users.crud import exportCrud as users_crud
from app.organizations.crud import exportCrud as organizations_crud
from sqlalchemy import or_, and_
from fastapi.encoders import jsonable_encoder


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamPatch]):
    async def get_multi(self, db: Session, user_id: str, and_public: bool = False, or_public: bool = False, organization_id: uuid.UUID = None) -> Optional[List[Team]]:
        queries = []
        if user_id:
            queries.append(
                or_(
                    Team.users.any(models.User.id.in_([user_id])),
                    Team.administrators.any(models.User.id.in_([user_id]))
                )
            )
        if organization_id:
            queries.append(Team.organization_id == organization_id)

        result = db.query(
                Team
            ).filter(*queries)

        if and_public and organization_id:
            public_query = db.query(
                Team
            ).filter(
                Team.public == True,
                Team.organization_id == organization_id
            )
            result = result.union(public_query)

        if or_public:
            public_query2 = db.query(
                Team
            ).filter(
                Team.public == True
            ).filter(
                models.Organization.id == Team.organization_id
            ).filter(
                models.Organization.public == True
            )
            result = result.union(public_query2)
        return result.all()

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
        team.users.remove(user)
        db.commit()
        db.refresh(team)
        await log(self.enrich_log_data(team, {
            "model": "TEAM",
            "action": "REMOVE_USER",
            "removed_user_id": user.id
        }))
        return team

    async def create(self, db: Session, obj_in: TeamCreate, creator: models.User) -> Team:
        obj_in_data = jsonable_encoder(obj_in)
        user_ids = obj_in.user_ids
        del obj_in_data["user_ids"]
        
        db_obj = Team(**obj_in_data)
        db_obj.creator_id = creator.id
        db_obj.administrators.append(creator)
        for user in await users_crud.get_multi_by_ids(db=db, ids=user_ids):
            db_obj.users.append(user)

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
    async def can_create(self, db: Session, organization_id: uuid.UUID, user: models.User):
        org = await organizations_crud.get(db=db, id=organization_id)
        if org:
            if org.team_creation_permission == models.TeamCreationPermissions.anyone:
                return True
            elif org.team_creation_permission == models.TeamCreationPermissions.administrators:
                return user in org.administrators
            elif org.team_creation_permission == models.TeamCreationPermissions.members:
                return org in db.query(models.Organization).join(Team).filter(
                    Team.id.in_(user.teams_ids)
                ).all()
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

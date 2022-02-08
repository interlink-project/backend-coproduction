from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import Team
from app.schemas import TeamCreate, TeamPatch
import uuid


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamPatch]):
    def get_by_name(self, db: Session, name: str) -> Optional[Team]:
        return db.query(Team).filter(Team.name == name).first()

    def create(self, db: Session, *, team: TeamCreate) -> Team:
        db_obj = Team(
            name_translations=team.name_translations,
            description_translations=team.description_translations,
            logotype=team.logotype,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    """
    def add_user(self, db: Session, *, team: Team, user: User) -> Team:            
        team.users.append(user)
        db.commit()
        db.refresh(team)
        return team

    def delete_user(self, db: Session, *, team: Team, user: User) -> Team:            
        team.users.remove(user)
        db.commit()
        db.refresh(team)
        return team
        
        
    # Specific
    def can_modify_users(self, user, object):
        return True

        
    #######
    # Users relation
    #######


    @router.put("/{id}/users/{user_id}", response_model=schemas.TeamOutFull)
    def add_user_to_team(
        *,
        db: Session = Depends(deps.get_db),
        id: uuid.UUID,
        user_id: uuid.UUID,
        current_user: models.User = Depends(deps.get_current_active_user),
    ) -> Any:
        team = crud.team.get(db=db, id=id)
        user = crud.user.get(db=db, id=user_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user in team.users:
            raise HTTPException(status_code=404, detail="User already in team")
        if not crud.team.can_modify_users(current_user, team):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return crud.team.add_user(db=db, team=team, user=user)


    @router.delete("/{id}/users/{user_id}", response_model=schemas.TeamOutFull)
    def delete_user_from_team(
        *,
        db: Session = Depends(deps.get_db),
        id: uuid.UUID,
        user_id: uuid.UUID,
        current_user: models.User = Depends(deps.get_current_active_user),
    ) -> Any:
        team = crud.team.get(db=db, id=id)
        user = crud.user.get(db=db, id=user_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user in team.users:
            raise HTTPException(status_code=400, detail="User not in team")
        if not crud.team.can_modify_users(current_user, team):
            raise HTTPException(status_code=403, detail="Not enough permissions")
            
        return crud.team.delete_user(db=db, team=team, user=user)
    """

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

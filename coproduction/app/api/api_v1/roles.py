import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()

class RoleSwitch(BaseModel):
    new_role: uuid.UUID
    old_role: uuid.UUID
    team_id: Optional[uuid.UUID]
    user_id: Optional[uuid.UUID]

@router.post("/switch")
def switch_role(
    *,
    db: Session = Depends(deps.get_db),
    switch_in: RoleSwitch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Switch roles
    """
    user = None
    team = None
    if switch_in.user_id and not (user := crud.user.get(db=db, id=switch_in.user_id)):
        raise HTTPException(status_code=400, detail="User does not exist")

    if switch_in.team_id and not (team := crud.team.get(db=db, id=switch_in.team_id)):
        raise HTTPException(status_code=400, detail="Team does not exist")

    if not user and not team:
        raise HTTPException(status_code=400, detail="Please, specify a team or a user")
    if user and team:
        raise HTTPException(status_code=400, detail="Please, specify only a team or a user")

    new_role = crud.role.get(db=db, id=switch_in.new_role)
    old_role = crud.role.get(db=db, id=switch_in.old_role)
    if not old_role or not new_role:
        raise HTTPException(status_code=400, detail="At least one of the roles does not exist")
    
    if new_role.coproductionprocess_id != old_role.coproductionprocess_id:
        raise HTTPException(status_code=400, detail="Creators role can not be modified")
    if old_role.coproductionprocess.creator_id == switch_in.user_id:
        raise HTTPException(status_code=400, detail="Role of the creator can not be modified")

    if user:
        old_role.users.remove(user)
        new_role.users.append(user)
    if team:
        old_role.teams.remove(team)
        new_role.teams.append(team)
    
    db.commit()
    return True
    
@router.post("", response_model=schemas.RoleOut)
def create_role(
    *,
    db: Session = Depends(deps.get_db),
    role: schemas.RoleCreate,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Create role
    """
    return crud.role.create(db=db, role=role)

@router.get("", response_model=List[schemas.RoleOutFull])
def get_roles(
    *,
    db: Session = Depends(deps.get_db),
    coproductionprocess_id: uuid.UUID = Query(None),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get role by ID.
    """
    if process := crud.coproductionprocess.get(db=db, id=coproductionprocess_id):
        return process.roles
    raise HTTPException(status_code=404, detail="Coproductionprocess not found")

@router.get("/2")
def get_roles2(
    *,
    db: Session = Depends(deps.get_db),
    coproductionprocess_id: uuid.UUID = Query(None),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get role by ID.
    """
    if process := crud.coproductionprocess.get(db=db, id=coproductionprocess_id):
        return crud.role.get_permissions_of_user_for_coproductionprocess(db=db, coproductionprocess=process, user=current_user)
    raise HTTPException(status_code=404, detail="Coproductionprocess not found")

@router.get("/{id}", response_model=schemas.RoleOutFull)
def get_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get role by ID.
    """
    if role := crud.role.get(db=db, id=id):
        return role
    raise HTTPException(status_code=404, detail="Role not found")

@router.put("/{id}", response_model=schemas.RoleOutFull)
def update_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    role_in: schemas.RolePatch,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Patch role by ID.
    """
    if role := crud.role.get(db=db, id=id):
        return crud.role.update(db=db, db_obj=role, obj_in=role_in)
    raise HTTPException(status_code=404, detail="Role not found")


@router.delete("/{id}")
def delete_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Delete role by ID.
    """
    if role := crud.role.get(db=db, id=id):
        return crud.role.remove(db=db, id=role.id)
    raise HTTPException(status_code=404, detail="Role not found")
 
class TeamIn(BaseModel):
    team_id: uuid.UUID

@router.post("/{id}/add_team")
def add_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    team_in: TeamIn,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add team to role
    """
    if role := crud.role.get(db=db, id=id):
        if team := crud.team.get(db=db, id=team_in.team_id):
            crud.role.add_team(db=db, role=role, team=team)
            return True
        raise HTTPException(status_code=400, detail="Team not found")
    raise HTTPException(status_code=404, detail="Role not found")


@router.post("/{id}/remove_team")
def remove_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    team_in: TeamIn,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add team to role
    """
    if role := crud.role.get(db=db, id=id):
        if team := crud.team.get(db=db, id=team_in.team_id):
            crud.role.remove_team(db=db, role=role, team=team)
            return True
        raise HTTPException(status_code=400, detail="Team not found")
    raise HTTPException(status_code=404, detail="Role not found")
    
    
class UserIn(BaseModel):
    user_id: str

@router.post("/{id}/remove_user")
def remove_user(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    user_in: UserIn,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add user to role
    """
    if role := crud.role.get(db=db, id=id):
        if user := crud.user.get(db=db, id=user_in.user_id):
            crud.role.remove_user(db=db, role=role, user=user)
            return True
        raise HTTPException(status_code=400, detail="User not found")
    raise HTTPException(status_code=404, detail="Role not found")
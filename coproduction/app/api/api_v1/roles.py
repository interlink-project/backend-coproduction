import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

from app.messages import log

router = APIRouter()

class RoleSwitch(BaseModel):
    new_role: uuid.UUID
    old_role: uuid.UUID
    team_id: Optional[uuid.UUID]
    user_id: Optional[str]

@router.post("/switch")
async def switch_role(
    *,
    db: Session = Depends(deps.get_db),
    switch_in: RoleSwitch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Switch roles
    """
    user = None
    team = None
    if switch_in.user_id and not (user := await crud.user.get(db=db, id=switch_in.user_id)):
        raise HTTPException(status_code=400, detail="User does not exist")

    if switch_in.team_id and not (team := await crud.team.get(db=db, id=switch_in.team_id)):
        raise HTTPException(status_code=400, detail="Team does not exist")

    if not user and not team:
        raise HTTPException(status_code=400, detail="Please, specify a team or a user")
    if user and team:
        raise HTTPException(status_code=400, detail="Please, specify only a team or a user")

    new_role = await crud.role.get(db=db, id=switch_in.new_role)
    old_role = await crud.role.get(db=db, id=switch_in.old_role)
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
async def create_role(
    *,
    db: Session = Depends(deps.get_db),
    role: schemas.RoleCreate,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Create role
    """

    role = await crud.role.create(db=db, role=role)

    await log({
        "model": "ROLE",
        "action": "CREATE",
        "crud": False,
        "coproductionprocess_id": role.coproductionprocess_id,
        "rol_id": role.id
    })


    return role

@router.get("", response_model=List[schemas.RoleOutFull])
async def get_roles(
    *,
    db: Session = Depends(deps.get_db),
    coproductionprocess_id: uuid.UUID = Query(None),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get role by ID.
    """
    if process := await crud.coproductionprocess.get(db=db, id=coproductionprocess_id):

        return process.roles

    raise HTTPException(status_code=404, detail="Coproductionprocess not found")

@router.get("/{id}", response_model=schemas.RoleOutFull)
async def get_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get role by ID.
    """
    if role := await crud.role.get(db=db, id=id):

        await log({
            "model": "ROLE",
            "action": "GET",
            "crud": False,
            "coproductionprocess_id": role.coproductionprocess_id,
            "rol_id": role.id
        })

        return role

    raise HTTPException(status_code=404, detail="Role not found")

@router.put("/{id}", response_model=schemas.RoleOutFull)
async def update_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    role_in: schemas.RolePatch,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Patch role by ID.
    """
    if role := await crud.role.get(db=db, id=id):

        await log({
            "model": "ROLE",
            "action": "UPDATE",
            "crud": False,
            "coproductionprocess_id": role.coproductionprocess_id,
            "rol_id": role.id
        })

        return await crud.role.update(db=db, db_obj=role, obj_in=role_in)

    raise HTTPException(status_code=404, detail="Role not found")


@router.delete("/{id}")
async def delete_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Delete role by ID.
    """
    if role := await crud.role.get(db=db, id=id):

        await log({
            "model": "ROLE",
            "action": "DELETE ROLE",
            "crud": False,
            "coproductionprocess_id": role.coproductionprocess_id,
            "rol_id": role.id
        })

        return await crud.role.remove(db=db, id=role.id)

    raise HTTPException(status_code=404, detail="Role not found")
 
class TeamIn(BaseModel):
    team_id: uuid.UUID

@router.post("/{id}/add_team")
async def add_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    team_in: TeamIn,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add team to role
    """
    if role := await crud.role.get(db=db, id=id):
        if team := await crud.team.get(db=db, id=team_in.team_id):
            await crud.role.add_team(db=db, role=role, team=team)

            await log({
                "model": "ROLE",
                "action": "CREATE",
                "crud": False,
                "coproductionprocess_id": role.coproductionprocess_id,
                "team_id": team.id,
                "rol_id": role.id
            })
            return True
        raise HTTPException(status_code=400, detail="Team not found")

    raise HTTPException(status_code=404, detail="Role not found")


@router.post("/{id}/remove_team")
async def remove_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    team_in: TeamIn,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add team to role
    """
    if role := await crud.role.get(db=db, id=id):
        if team := await crud.team.get(db=db, id=team_in.team_id):

            await log({
                "model": "ROLE",
                "action": "REMOVE TEAM",
                "crud": False,
                "coproductionprocess_id": role.coproductionprocess_id,
                "team_id": team.id,
                "rol_id": role.id
            })

            await crud.role.remove_team(db=db, role=role, team=team)
            return True
        raise HTTPException(status_code=400, detail="Team not found")

    raise HTTPException(status_code=404, detail="Role not found")
    
    
class UserIn(BaseModel):
    user_id: str

@router.post("/{id}/remove_user")
async def remove_user(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    user_in: UserIn,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add user to role
    """
    if role := await crud.role.get(db=db, id=id):
        if user := await crud.user.get(db=db, id=user_in.user_id):

            await log({
                "model": "ROLE",
                "action": "DELETE USER",
                "crud": False,
                "coproductionprocess_id": role.coproductionprocess_id,
                "user_id": user.id,
                "rol_id": role.id
            })

            await crud.role.remove_user(db=db, role=role, user=user)

            return True
        raise HTTPException(status_code=400, detail="User not found")

    raise HTTPException(status_code=404, detail="Role not found")
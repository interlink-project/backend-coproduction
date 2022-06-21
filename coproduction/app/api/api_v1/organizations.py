import os
import uuid
from typing import Any, List, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps
from app.messages import log

router = APIRouter()


@router.get("", response_model=List[schemas.OrganizationOutFull])
async def list_organizations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
    search: str = Query(None)
) -> Any:
    """
    Retrieve organizations.
    """
    if not crud.organization.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.organization.get_multi(db, skip=skip, limit=limit, user=current_user, search=search)


@router.post("", response_model=schemas.OrganizationOutFull)
async def create_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_in: schemas.OrganizationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new organization.
    """
    if not crud.organization.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.organization.create(db=db, obj_in=organization_in, creator=current_user, set_creator_admin=True)


@router.get("/{id}/objectives", response_model=List[schemas.ObjectiveOut])
async def list_related_objectives(
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve related objectives.
    """
    organization = await crud.organization.get(db, id=id)
    if not organization:
        raise HTTPException(status_code=400, detail="Organization not found")
    return organization.objectives


@router.put("/{id}", response_model=schemas.OrganizationOutFull)
async def update_organization(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    organization_in: schemas.OrganizationPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an organization.
    """
    organization = await crud.organization.get(db=db, id=id)

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not crud.organization.can_update(current_user, organization):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.organization.update(db=db, db_obj=organization, obj_in=organization_in)


@router.get("/{id}", response_model=schemas.OrganizationOutFull)
async def read_organization(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get organization by ID.
    """
    organization = await crud.organization.get(db=db, id=id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not await crud.organization.can_read(db=db, user=current_user, object=organization):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return organization


@router.get("/{id}/teams", response_model=List[schemas.TeamOutFull])
async def read_organization_teams(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization by ID.
    """
    organization = await crud.organization.get(db=db, id=id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not await crud.organization.can_read(db=db, user=current_user, object=organization):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.team.get_multi(db=db, user=current_user, organization=organization)


@router.delete("/{id}")
async def delete_organization(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an organization.
    """
    organization = await crud.organization.get(db=db, id=id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not crud.organization.can_remove(current_user, organization):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await crud.organization.remove(db=db, id=id)
    return None


@router.post("/{id}/logotype")
async def set_logotype(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
) -> Any:
    if (organization := await crud.organization.get(db=db, id=id)):
        if crud.organization.can_update(user=current_user, object=organization):
            filename, extension = os.path.splitext(file.filename)
            out_file_path = f"/static/organizations/{organization.id}{extension}"

            async with aiofiles.open("/app" + out_file_path, 'wb') as out_file:
                content = await file.read()  # async read
                await out_file.write(content)  # async write
            return await crud.organization.update(db=db, db_obj=organization, obj_in=schemas.OrganizationPatch(logotype=out_file_path))
        raise HTTPException(
            status_code=403, detail="You are not allowed to update this organization")
    raise HTTPException(status_code=404, detail="Organization not found")

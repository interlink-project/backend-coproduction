from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

from app.messages import log

router = APIRouter()


@router.get("", response_model=List[schemas.TreeItemOut])
async def list_treeitems(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve treeitems.
    """
    if not crud.treeitem.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    treeitem = await crud.treeitem.get_multi(db, skip=skip, limit=limit)

    return treeitem


@router.post("", response_model=schemas.TreeItemOutFull)
async def create_treeitem(
    *,
    db: Session = Depends(deps.get_db),
    treeitem_in: schemas.TreeItemCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new treeitem.
    """
    if not crud.treeitem.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    treeitem = await crud.treeitem.create(db=db, treeitem=treeitem_in)

    await log({
        "model": "TREEITEM",
        "action": "CREATE",
        "crud": False,
        "coproductionprocess_id": treeitem.coproductionprocess_id,
        "treeitem_id": treeitem.id
    })

    return treeitem


@router.put("/{id}", response_model=schemas.TreeItemOutFull)
async def update_treeitem(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    treeitem_in: schemas.TreeItemPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an treeitem.
    """
    treeitem = await crud.treeitem.get(db=db, id=id)

    if not treeitem:
        raise HTTPException(status_code=404, detail="TreeItem not found")
    if not crud.treeitem.can_update(current_user, treeitem):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    treeitem = await crud.treeitem.update(db=db, db_obj=treeitem, obj_in=treeitem_in)

    await log({
        "model": "TREEITEM",
        "action": "UPDATE",
        "crud": False,
        "coproductionprocess_id": treeitem.coproductionprocess_id,
        "treeitem_id": treeitem.id
    })

    return treeitem


@router.get("/{id}", response_model=schemas.TreeItemOutFull)
async def read_treeitem(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get treeitem by ID.
    """
    treeitem = await crud.treeitem.get(db=db, id=id)

    await log({
        "model": "TREEITEM",
        "action": "GET",
        "crud": False,
        "coproductionprocess_id": treeitem.coproductionprocess_id,
        "treeitem_id": treeitem.id
    })
    if not treeitem:
        raise HTTPException(status_code=404, detail="TreeItem not found")
    if not crud.treeitem.can_read(current_user, treeitem):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return treeitem


@router.delete("/{id}", response_model=schemas.TreeItemOutFull)
async def delete_treeitem(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an treeitem.
    """
    treeitem = await crud.treeitem.get(db=db, id=id)

    if not treeitem:
        raise HTTPException(status_code=404, detail="TreeItem not found")
    if not crud.treeitem.can_remove(current_user, treeitem):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await log({
        "model": "TREEITEM",
        "action": "DELETE",
        "crud": False,
        "coproductionprocess_id": treeitem.coproductionprocess_id,
        "treeitem_id": treeitem.id
    })
    await crud.treeitem.remove(db=db, id=id)

    await log({
        "model": "TREEITEM",
        "action": "DELETE",
        "crud": False,
        "coproductionprocess_id": treeitem.coproductionprocess_id,
        "treeitem_id": treeitem.id
    })

    return None
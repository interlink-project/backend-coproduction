from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.CoproductionSchemaOut])
def list_coproductionschemas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve coproductionschemas.
    """
    if not crud.coproductionschema.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    coproductionschemas = crud.coproductionschema.get_multi(db, skip=skip, limit=limit)
    return coproductionschemas


@router.post("/", response_model=schemas.CoproductionSchemaOutFull)
def create_coproductionschema(
    *,
    db: Session = Depends(deps.get_db),
    coproductionschema_in: schemas.CoproductionSchemaCreate,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new coproductionschema.
    """
    if not crud.coproductionschema.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    coproductionschema = crud.coproductionschema.create(db=db, coproductionschema=coproductionschema_in)
    return coproductionschema


@router.put("/{id}", response_model=schemas.CoproductionSchemaOutFull)
def update_coproductionschema(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    coproductionschema_in: schemas.CoproductionSchemaPatch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an coproductionschema.
    """
    coproductionschema = crud.coproductionschema.get(db=db, id=id)
    if not coproductionschema:
        raise HTTPException(status_code=404, detail="CoproductionSchema not found")
    if not crud.coproductionschema.can_update(current_user, coproductionschema):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    coproductionschema = crud.coproductionschema.update(db=db, db_obj=coproductionschema, obj_in=coproductionschema_in)
    return coproductionschema


@router.get("/{id}", response_model=schemas.CoproductionSchemaOutFull)
def read_coproductionschema(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Get coproductionschema by ID.
    """
    coproductionschema = crud.coproductionschema.get(db=db, id=id)
    if not coproductionschema:
        raise HTTPException(status_code=404, detail="CoproductionSchema not found")
    if not crud.coproductionschema.can_read(current_user, coproductionschema):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return coproductionschema


@router.delete("/{id}", response_model=schemas.CoproductionSchemaOutFull)
def delete_coproductionschema(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an coproductionschema.
    """
    coproductionschema = crud.coproductionschema.get(db=db, id=id)
    if not coproductionschema:
        raise HTTPException(status_code=404, detail="CoproductionSchema not found")
    if not crud.coproductionschema.can_remove(current_user, coproductionschema):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.coproductionschema.remove(db=db, id=id)
    return None

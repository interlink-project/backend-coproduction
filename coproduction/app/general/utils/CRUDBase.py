import logging
import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.general.db.base_class import Base
from app.messages import log
from app.middleware import get_user_id

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
PatchSchemaType = TypeVar("PatchSchemaType", bound=BaseModel)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDBase(Generic[ModelType, CreateSchemaType, PatchSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Patch, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.modelName = model.__name__.upper()
        self.model = model

    async def get(self, db: Session, id: uuid.UUID) -> Optional[ModelType]:
        await log({
            "type": f"{self.modelName}_GET",
            "id": str(id)
        })
        return db.query(self.model).filter(self.model.id == id).first()

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        await log({
            "type": f"{self.modelName}_LIST"
        })
        return db.query(self.model).order_by(self.model.created_at.asc()).offset(skip).limit(limit).all()

    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        log({
            "type": f"{self.modelName}_CREATE",
            "id": str(db_obj.id)
        })
        db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[PatchSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        await log({
            "type": f"{self.modelName}_UPDATE",
            "id": obj_in.id
        })
        db.refresh(db_obj)
        return db_obj

    async def remove(self, db: Session, *, id: uuid.UUID) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        await log({
            "type": f"{self.modelName}_REMOVE",
            "id": str(id)
        })
        return obj

    # CRUD Permissions
    def can_create(self, user):
        logger.warn("You need to override can_create of the crud")
        return True

    def can_list(self, user):
        logger.warn("You need to override can_list of the crud")
        return True

    def can_read(self, user, object):
        logger.warn("You need to override can_read of the crud")
        return True

    def can_update(self, user, object):
        logger.warn("You need to override can_update of the crud")
        return True

    def can_remove(self, user, object):
        logger.warn("You need to override can_remove of the crud")
        return True

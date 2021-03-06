import logging
import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException

from app.general.db.base_class import Base
from app.messages import log
from app.users.models import User
from app.config import settings

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
PatchSchemaType = TypeVar("PatchSchemaType", bound=BaseModel)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDBase(Generic[ModelType, CreateSchemaType, PatchSchemaType]):
    def __init__(self, model: Type[ModelType], logByDefault=False):
        """
        CRUD object with default methods to Create, Read, Patch, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.logByDefault = logByDefault
        self.modelName = model.__name__.upper()
        self.model = model

    async def get(self, db: Session, id: uuid.UUID) -> Optional[ModelType]:
        if obj := db.query(self.model).filter(self.model.id == id).first():
            await self.log_on_get(obj)
            return obj
        return

    async def get_multi_by_ids(self, db: Session, ids: list) -> List[ModelType]:
        return db.query(self.model).filter(self.model.id.in_(ids)).all()

    async def get_by_name(self, db: Session, name: str) -> Optional[ModelType]:
        if obj := db.query(self.model).filter(self.model.name == name).first():
            await self.log_on_get(obj)
            return obj
        return

    async def get_by_name_translation(self, db: Session, name: str, language: str = settings.DEFAULT_LANGUAGE) -> Optional[ModelType]:
        if obj := db.query(self.model).filter(self.model.name_translations[language] == name).first():
            await self.log_on_get(obj)
            return obj
        return

    async def get_by_name_translations(self, db: Session, name_translations: str) -> Optional[ModelType]:
        return db.query(self.model).filter(
            or_(
                and_(self.model.name_translations["en"] != None, self.model.name_translations["en"] == name_translations["en"]),
                and_(self.model.name_translations["es"] != None, self.model.name_translations["es"] == name_translations["es"]),
                and_(self.model.name_translations["it"] != None, self.model.name_translations["it"] == name_translations["it"]),
                and_(self.model.name_translations["lv"] != None, self.model.name_translations["lv"] == name_translations["lv"]),
            ),
        ).first()

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).order_by(self.model.created_at.asc()).offset(skip).limit(limit).all()

    async def create(self, db: Session, *, obj_in: CreateSchemaType, creator: User = None, set_creator_admin: bool = False, extra: dict = {}, commit: bool = True) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, **extra)  # type: ignore

        if creator:
            db_obj.creator_id = creator.id
            if set_creator_admin:
                db_obj.administrators.append(creator)

        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
            await self.log_on_create(db_obj)
        return db_obj

    async def add_administrator(self, db: Session, *, db_obj: ModelType, user: User = None) -> ModelType:
        db_obj.administrators.append(user)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        enriched: dict = self.enrich_log_data(db_obj, {
            "action": "ADD_ADMINISTRATOR",
            "added_user_id": user.id
        })
        await log(enriched)
        return db_obj

    async def remove_administrator(self, db: Session, *, db_obj: ModelType, user: User = None) -> ModelType:
        if len(db_obj.administrators) <= 1:
            raise HTTPException(status_code=400, detail="Can not delete the last administrator")

        db_obj.administrators.remove(user)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        enriched: dict = self.enrich_log_data(db_obj, {
            "action": "REMOVE_ADMINISTRATOR",
            "removed_user_id": user.id
        })
        await log(enriched)
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
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value != getattr(db_obj, field):
                print("Updating", field)
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        await self.log_on_update(db_obj)
        return db_obj

    async def remove(self, db: Session, *, id: uuid.UUID) -> ModelType:
        obj = db.query(self.model).get(id)
        await self.log_on_remove(obj)
        db.delete(obj)
        db.commit()
        return obj

    # LOGS
    async def log_on_get(self, obj):
        # enriched : dict  = self.enrich_log_data(obj, {
        #     "action": "GET"
        # })
        # await log(enriched)
        pass

    async def log_on_create(self, obj):
        enriched: dict = self.enrich_log_data(obj, {
            "action": "CREATE"
        })
        await log(enriched)

    async def log_on_update(self, obj):
        enriched: dict = self.enrich_log_data(obj, {
            "action": "UPDATE"
        })
        await log(enriched)

    async def log_on_remove(self, obj):
        enriched: dict = self.enrich_log_data(obj, {
            "action": "DELETE"
        })
        await log(enriched)

    def enrich_log_data(self, obj, logData) -> dict:
        logData["model"] = self.modelName
        logData["object_id"] = obj.id
        return logData

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

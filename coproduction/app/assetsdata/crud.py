from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app import models
from app.schemas import AssetsDataCreate, AssetsDataPatch, AssetsDataOutFull
import uuid
from sqlalchemy import and_, func, or_
from app.treeitems.crud import exportCrud as treeitemsCrud
from fastapi.encoders import jsonable_encoder


class CRUDAssetsData(CRUDBase[models.AssetsData, AssetsDataCreate, AssetsDataPatch]):
    
    async def get(self, db: Session, id: uuid.UUID) -> Optional[models.AssetsData]:
        if obj := db.query(models.AssetsData).filter(
                models.AssetsData.id == id,
        ).first():
            await self.log_on_get(obj)
            return obj
        return

    async def getAssetsData(self, db: Session, id: str) -> Optional[models.AssetsData]:
        if obj := db.query(models.AssetsData).filter(
            models.AssetsData.id == id,
        ).first():
            return obj
        return
        


exportCrud = CRUDAssetsData(models.AssetsData, logByDefault=True)

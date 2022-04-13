import requests
from sqlalchemy.orm import Session
from typing import List
from app.models import Asset, InternalAsset, ExternalAsset
from app.schemas import AssetCreate, AssetPatch, ExternalAssetCreate, InternalAssetCreate
from app.general.utils.CRUDBase import CRUDBase
from app import models
import uuid
from app.messages import log
from fastapi.encoders import jsonable_encoder
import favicon

class CRUDAsset(CRUDBase[Asset, AssetCreate, AssetPatch]):

    async def get_multi_filtered(
        self, db: Session, coproductionprocess_id: uuid.UUID, task_id: uuid.UUID
    ) -> List[Asset]:
        queries = []
        if coproductionprocess_id:
            queries.append(Asset.coproductionprocess_id == coproductionprocess_id)
        
        if task_id:
            queries.append(Asset.task_id == task_id)
        # await log({
        #     "model": self.modelName,
        #     "action": "LIST",
        #     "coproductionprocess_id": coproductionprocess_id,
        #     "task_id": task_id
        # })
        return db.query(Asset).filter(*queries).all()
    
    async def create(self, db: Session, asset: AssetCreate, coproductionprocess_id: uuid.UUID, creator: models.User) -> Asset:
        data = jsonable_encoder(asset)
        if type(asset) == ExternalAssetCreate:
            print("IS EXTERNAL")
            data["type"] = "externalasset"

            # try to get favicon
            try:
                icons = favicon.get(asset.uri)
                if len(icons) > 0 and (icon := icons[0]) and icon.format:
                    response = requests.get(icon.url, stream=True)
                    
                    icon_path = f'/app/static/assets/{uuid.uuid4()}.{icon.format}'
                    with open(icon_path, 'wb') as image:
                        for chunk in response.iter_content(1024):
                            image.write(chunk)
                    icon_path = icon_path.replace("/app", "")
                    print(icon_path)
                    data["icon_path"] = icon_path
            except:
                pass
            db_obj = ExternalAsset(**data, creator=creator, coproductionprocess_id=coproductionprocess_id)

        if type(asset) == InternalAssetCreate:
            print("IS INTERNAL")
            data["type"] = "internalasset"
            db_obj = InternalAsset(**data, creator=creator, coproductionprocess_id=coproductionprocess_id)

        db.add(db_obj)
        db.commit()
        # await log({
        #     "model": self.modelName,
        #     "action": "CREATE",
        #     "id": db_obj.id,
        #     "crud": True,
        #     "coproductionprocess_id": coproductionprocess_id,
        #     "task_id": db_obj.task_id
        # })
        db.refresh(db_obj)
        if type(asset) == InternalAssetCreate:
            db_obj.set_links()
        return db_obj
    
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

exportCrud = CRUDAsset(Asset)
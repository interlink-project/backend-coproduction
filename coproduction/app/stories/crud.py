from app.messages import log
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import Notification, Story, User, Organization
from app.schemas import NotificationCreate, NotificationPatch, StoryCreate, StoryPatch
import uuid
from app import models
from app.users.crud import exportCrud as users_crud
from app.assets.crud import exportCrud as assets_crud
from app.treeitems.crud import exportCrud as treeitems_crud

from sqlalchemy import and_, func, or_
from fastapi.encoders import jsonable_encoder
from app.sockets import socket_manager
from uuid_by_string import generate_uuid
from fastapi_pagination.ext.sqlalchemy import paginate
from app import schemas
import json


class CRUDStory(CRUDBase[Story, StoryCreate, StoryPatch]):

  
    async def get_multiDict(
        self, db: Session, exclude: list = [], search: str = "", rating: int = 0, language: str = "en"
    ) -> List[Story]:
        queries = []

        
        # if language:
        #     queries.append(Story.languages.any(language))
        
        # if problemprofiles:
        #     queries.append(Story.problemprofiles.any(ProblemProfile.id.in_(problemprofiles)))

        if rating:
            queries.append(Story.rating >= rating)
            
        if search:
            search = search.lower()
            queries.append(or_(
                    # func.lower(Story.tags_translations[language]).contains(
                    #     search),
                    func.lower(Story.data_story['title'].astext).contains(func.lower(
                        search)),
                    func.lower(
                        Story.data_story['description'].astext).contains(func.lower(search))
                ))
        
        # if natures:
        #     queries.append(
        #         Interlinker.nature.in_(natures)
        #     )
        
        # if creator:
        #     queries.append(
        #         Interlinker.creator_id != None
        #     )
        return paginate(db.query(Story).filter(*queries, Story.id.not_in(exclude)))
        #return paginate(db.query(Story).all())




    async def get_multi(self, db: Session, user: User) -> Optional[List[Story]]:
        return db.query(Story).all()

    #Get all stories by user:
    async def get_coproductionprocess_stories(self, db: Session, coproductionprocess_id: str,user) -> Optional[List[Story]]:
        
        listofStories = db.query(Story).filter(models.Story.coproductionprocess_id==coproductionprocess_id).order_by(models.Story.created_at.desc()).all()

        return listofStories


    async def create(self, db: Session, obj_in: StoryCreate) -> Story:
        obj_in_data = jsonable_encoder(obj_in)
        
        db_obj = Story(**obj_in_data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        await socket_manager.broadcast({"event": "story_created"})

        await self.log_on_create(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        db_obj: Story,
        obj_in: schemas.StoryPatch
    ) -> Story:
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
        db.refresh(db_obj)
        await self.log_on_update(db_obj)
        return db_obj
  
exportCrud = CRUDStory(Story)
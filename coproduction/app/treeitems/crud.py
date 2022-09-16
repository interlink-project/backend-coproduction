import uuid
from typing import List, Optional

from sqlalchemy.orm import Session
from app.models import TreeItem, Task, Objective, Phase
from app.utils import update_status_and_progress
from datetime import datetime
from app import models
from sqlalchemy import or_
from app.sockets import socket_manager

class CRUDTreeItem:
    async def get(self, db: Session, id: uuid.UUID) -> Optional[TreeItem]:
        return db.query(TreeItem).filter(TreeItem.id == id).first()

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[TreeItem]:
        return db.query(TreeItem).order_by(TreeItem.created_at.asc()).offset(skip).limit(limit).all()
    
    async def get_for_user_and_coproductionprocess(
        self, db: Session, user: models.User, coproductionprocess_id: uuid.UUID
    ):
        return db.query(
                models.TreeItem
            ).join(
                models.Permission
            ).filter(
                models.Permission.treeitem_id == models.TreeItem.id,
                models.Permission.coproductionprocess_id == coproductionprocess_id
            ).filter(
                or_(
                    models.Permission.user_id == user.id,
                    models.Permission.team_id.in_(user.teams_ids)
                )
            ).all()
    
    async def get_for_teams(
        self, db: Session, teams_ids: List[uuid.UUID]
    ):
        return db.query(
                models.TreeItem
            ).join(
                models.Permission
            ).filter(
                or_(
                    models.Permission.team_id.in_(teams_ids)
                )
            ).all()

    async def remove(self, db: Session, obj, model, user_id: str = None, remove_definitely: bool = False) -> TreeItem:
        parent = None
        if model == Task:
            parent = obj.objective
        elif model == Objective:
            parent = obj.phase

        if remove_definitely:
            db.delete(obj)
            if parent:
                update_status_and_progress(parent)
                db.add(parent)
            db.commit()
            return obj
        
        if not user_id:
            raise Exception("User id needed to disable treeitem")
        # else disable
        setattr(obj, "disabled_on", datetime.now())
        setattr(obj, "disabler_id", user_id)
        if parent:
            update_status_and_progress(parent)
            db.add(parent)
        db.commit()
        if hasattr(obj, "coproductionprocess_id"):
            await socket_manager.send_to_id(obj.coproductionprocess_id, {"event": "treeitem_removed"})
        return obj

exportCrud = CRUDTreeItem()

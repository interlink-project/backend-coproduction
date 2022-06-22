import uuid
from typing import List, Optional

from sqlalchemy.orm import Session
from app.models import TreeItem, Task, Objective, Phase
from app.utils import update_status_and_progress
from datetime import datetime

class CRUDTreeItem:
    async def get(self, db: Session, id: uuid.UUID) -> Optional[TreeItem]:
        return db.query(TreeItem).filter(TreeItem.id == id).first()

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[TreeItem]:
        return db.query(TreeItem).order_by(TreeItem.created_at.asc()).offset(skip).limit(limit).all()
    

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
        return obj

exportCrud = CRUDTreeItem()

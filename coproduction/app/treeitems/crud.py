from typing import List, Optional
from .models import TreeItem
from .schemas import TreeItemCreate, TreeItemPatch
from app.general.utils.CRUDBase import CRUDBase
from sqlalchemy.orm import Session
import uuid
from app import models
from app.utils import recursive_check

class CRUDTreeItem(CRUDBase[TreeItem, TreeItemCreate, TreeItemPatch]):
    async def create(self, db: Session, *, creator: models.User = None, treeitem: TreeItemCreate, commit : bool = True) -> TreeItem:
        if not treeitem.parent_id and not treeitem.coproductionprocess_id:
            raise Exception("Parent or coproductionprocess_id not specified")
        db_obj = TreeItem(**treeitem.dict())
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
        return db_obj

    async def get_tree(self, db: Session, coproductionprocess_id: uuid.UUID) -> List[TreeItem]:
        return db.query(TreeItem).filter(TreeItem.coproductionprocess_id == coproductionprocess_id).all()

    async def add_prerequisite(self, db: Session, treeitem: TreeItem, prerequisite: TreeItem, commit : bool = True) -> TreeItem:
        if treeitem == prerequisite:
            raise Exception("Same object")

        recursive_check(treeitem.id, prerequisite)
        treeitem.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(treeitem)
        return treeitem

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

exportCrud = CRUDTreeItem(TreeItem)
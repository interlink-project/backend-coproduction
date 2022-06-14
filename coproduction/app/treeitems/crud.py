import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import TreeItem


class CRUDTreeItem:
    async def get(self, db: Session, id: uuid.UUID) -> Optional[TreeItem]:
        return db.query(TreeItem).filter(TreeItem.id == id).first()

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[TreeItem]:
        return db.query(TreeItem).order_by(TreeItem.created_at.asc()).offset(skip).limit(limit).all()


exportCrud = CRUDTreeItem()

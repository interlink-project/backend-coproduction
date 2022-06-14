from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app import models
from app.config import settings
from app.general.utils.CRUDBase import CRUDBase
from app.models import Organization
from app.schemas import OrganizationCreate, OrganizationPatch
from sqlalchemy import or_

class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationPatch]):
    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, user: models.User
    ) -> List[Organization]:
        query = db.query(Organization).filter(
            Organization.public == True,
        )
        if user:
            query2 = db.query(Organization).filter(
                    Organization.administrators.any(models.User.id.in_([user.id]))
                )
            query3 = db.query(Organization).join(models.Team).filter(
                    models.Team.id.in_(user.team_ids)
                )
            query = query.union(query2).union(query3) 
        return query.order_by(Organization.created_at.asc()).offset(skip).limit(limit).all()        

    async def get_by_name(self, db: Session, name: str, language: str = settings.DEFAULT_LANGUAGE) -> Optional[Organization]:
        # await log({
        #     "model": self.modelName,
        #     "action": "GET_BY_NAME",
        #     "crud": True,
        #     "name": name
        # })
        return db.query(Organization).filter(Organization.name_translations[language] == name).first()

    # Override log methods
    def enrich_log_data(self, organization, logData):
        logData["model"] = "ORGANIZATION"
        logData["object_id"] = organization.id
        logData["type"] = organization.type
        return logData

    # CRUD Permissions
    def can_create(self, user):
        return True

    def can_list(self, user):
        return True

    def check_perm(self, db: Session, user: models.User, object, perm):
        return True

    async def can_read(self, db: Session, user, object):
        return object in await self.get_multi(db=db, user=user)

    def can_update(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="update")

    def can_remove(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="delete")


exportCrud = CRUDOrganization(Organization, logByDefault=True)

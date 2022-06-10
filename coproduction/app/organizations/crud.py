import uuid
from typing import List, Optional

from slugify import slugify
from sqlalchemy.orm import Session

from app import crud, models
from app.general.utils.CRUDBase import CRUDBase
from app.models import Organization
from app.schemas import OrganizationCreate, OrganizationPatch

class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationPatch]):
    async def get_by_name(self, db: Session, name: str) -> Optional[Organization]:
        # await log({
        #     "model": self.modelName,
        #     "action": "GET_BY_NAME",
        #     "crud": True,
        #     "name": name
        # })
        return db.query(Organization).filter(Organization.name == name).first()

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

    def can_read(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="retrieve")

    def can_update(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="update")

    def can_remove(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="delete")


exportCrud = CRUDOrganization(Organization, logByDefault=True)

from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app import models
from app.config import settings
from app.general.utils.CRUDBase import CRUDBase
from app.models import Organization, Team
from app.schemas import OrganizationCreate, OrganizationPatch
from sqlalchemy import or_, func
from app.locales import get_language

class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationPatch]):
    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, user: models.User, search: str = None, language:str = get_language()
    ) -> List[Organization]:
        query = db.query(Organization).filter(
            Organization.public == True,
        )
        if user:
            query2 = db.query(Organization).filter(
                    Organization.administrators.any(models.User.id.in_([user.id]))
                )
            query3 = db.query(Organization).join(models.Team).filter(
                    models.Team.id.in_(user.teams_ids)
                )
            query = query.union(query2).union(query3)
        
        if search:
            query = query.filter(
                func.lower(Organization.name_translations[language]).contains(search),
            )

        return query.order_by(Organization.created_at.asc()).offset(skip).limit(limit).all()        

    # Override log methods
    def enrich_log_data(self, organization, logData):
        logData["model"] = "ORGANIZATION"
        logData["object_id"] = organization.id
        logData["type"] = organization.default_team_type
        return logData

    # CRUD Permissions
    def can_create(self, user):
        return True

    def can_list(self, user):
        return True

    async def can_read(self, db: Session, user, object):
        return True

    def can_update(self, user, object):
        return user in object.administrators

    def can_remove(self, user, object):
        return user in object.administrators


exportCrud = CRUDOrganization(Organization, logByDefault=True)

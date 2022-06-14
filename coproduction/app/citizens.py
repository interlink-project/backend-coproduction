from app.organizations.crud import exportCrud as crud
from app.organizations.schemas import OrganizationCreate
from app.organizations.models import OrganizationTypes, TeamCreationPermissions

async def get_or_create_citizens_org(db):
    if org := await crud.get_by_name(db=db, name="Citizens", language="en"):
        return org
    org = await crud.create(db=db, obj_in=OrganizationCreate(
        name_translations={
            "en": "Citizens",
            "es": "Ciudadanos"
        },
        description_translations={
            "en": "Citizens",
            "es": "Ciudadanos"
        },
        public=True,
        logotype="",
        type=OrganizationTypes.citizen.value,
        team_creation_permission=TeamCreationPermissions.anyone.value,
    ), creator=None)
    return org


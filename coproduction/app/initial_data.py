import asyncio
import logging
from app.general.db.session import SessionLocal
from app.messages import set_logging_disabled
from app.organizations.crud import exportCrud as crud
from app.organizations.schemas import OrganizationCreate, OrganizationPatch
from app.organizations.models import TeamCreationPermissions
from app.utils import RoleTypes

async def get_or_create_citizens_org(db):
    data = {
        "name_translations": {
            "en": "Citizens",
            "es": "Ciudadanos",
            "it": "Cittadini",
            "lv": "Pilsoņi"
        },
        "description_translations": {
            "en": "This public organization allows for the creation of citizen teams that can be added to the co-production processes.",
            "es": "Esta organización pública permite la creación de equipos de ciudadanos que podrán ser añadidos a los procesos de co-producción.",
            "it": "Questa organizzazione pubblica consente la creazione di gruppi di cittadini che possono essere aggiunti ai processi di co-produzione.",
            "lv": "Šī sabiedriskā organizācija ļauj izveidot pilsoņu komandas, kuras var iesaistīt kopražošanas procesos."
        },
        "public": True,
        "logotype": "/static/organizations/citizens.png",
        "default_team_type": RoleTypes.citizen.value,
        "team_creation_permission": TeamCreationPermissions.anyone.value,
    }
    if org := await crud.get_by_name_translations(db=db, name_translations=data["name_translations"]):
        print("UPDATING CITIZENS ORGANIZATION")
        return await crud.update(db=db, db_obj=org, obj_in=OrganizationPatch(**data))
    print("CREATING CITIZENS ORGANIZATION")
    return  await crud.create(db=db, obj_in=OrganizationCreate(**data), creator=None)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# in start-dev.sh and start-prod.sh it is made a git clone of https://github.com/interlink-project/interlinkers-data/

class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


async def init():
    db = SessionLocal()
    set_logging_disabled(True)
    await get_or_create_citizens_org(db=db)
    db.close()

if __name__ == "__main__":
    logger.info("Creating initial data")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    logger.info("Initial data created")
    

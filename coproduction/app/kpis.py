import asyncio
import logging
from app.models import *
from app.general.db.session import SessionLocal
from app.messages import set_logging_disabled
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.dialects import postgresql

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# https://drive.google.com/u/2/open?id=1VBpL3sIcYRdXbHLmfIs0aYiWYaerWVCH

show_queries = False

def divide(x, y):
    if y == 0:
        print("Y should be greater than 0", x, y)
    return x / y

def get_raw_query(q):
    if show_queries:
        print(str(q.statement.compile(dialect=postgresql.dialect()))) 


def add(data, key, value):
    if key in data:
        return Exception("Key already present")
    data[key] = value

async def init():
    data = {}

    db: Session = SessionLocal()
    set_logging_disabled(True)

    # Coproductionprocesses count
    coproductionprocesses_count_query = db.query(
            CoproductionProcess.id
        )
    coproductionprocesses_count = coproductionprocesses_count_query.count()
    
    get_raw_query(coproductionprocesses_count_query)
    add(data, "Number of coproductionprocesses:", coproductionprocesses_count)

    # Resources count
    assets_count_query = db.query(
            Asset.id
        )
    assets_count = assets_count_query.count()

    get_raw_query(coproductionprocesses_count_query)
    add(data, "Number of assets created:", assets_count)

    # Users count
    users_count_query = db.query(
            User.id
        )
    users_count = users_count_query.count()

    get_raw_query(coproductionprocesses_count_query)
    add(data, "Number of users registered:", users_count)

    # Teams count
    teams_count_query = db.query(
            Team.id
        )
    teams_count = teams_count_query.count()

    get_raw_query(coproductionprocesses_count_query)
    add(data, "Number of teams created:", teams_count)

    # Means
    add(data, "Mean of assets per coproductionprocess:", divide(assets_count, coproductionprocesses_count))
    add(data, "Mean of users per team:", divide(teams_count, users_count))

    # Languages
    languages_query = db.query(
            CoproductionProcess.language
        ).group_by(CoproductionProcess.language)
    languages = languages_query.all()

    get_raw_query(languages_query)
    add(data, "Different languages used:", languages)

    for key in ["en", "es", "it", "lv"]:
        languages_query = db.query(
                CoproductionProcess.language
            ).filter(CoproductionProcess.language == key)
        languages = languages_query.count()

        get_raw_query(languages_query)
        add(data, f"Processes in {key} language:", languages)

    # ASSETS
    number_of_assets_query = db.query(
            Asset.id,
        )
    number_of_assets_query_count = number_of_assets_query.count()

    get_raw_query(number_of_assets_query)
    add(data, "Number of assets:", number_of_assets_query_count)

    internal_assets_query = db.query(
            InternalAsset.id,
        )
    internal_assets_query_count = internal_assets_query.count()

    get_raw_query(internal_assets_query)
    add(data, "Number of internal assets:", internal_assets_query_count)

    external_assets_query = db.query(
            ExternalAsset.id,
        )
    external_assets_query_count = external_assets_query.count()

    get_raw_query(external_assets_query)
    add(data, "Number of external assets:", external_assets_query_count)
    

    # SOFTWARE INTERLINKERS
    used_software_interlinkers_query = db.query(
            InternalAsset.softwareinterlinker_id,
        ).group_by(InternalAsset.softwareinterlinker_id)
    used_software_interlinkers_query_all = used_software_interlinkers_query.all()
    used_software_interlinkers_query_count = used_software_interlinkers_query.count()

    get_raw_query(used_software_interlinkers_query)
    add(data, "Used software interlinkers:", used_software_interlinkers_query_all)
    add(data, "Number of used software interlinkers:", used_software_interlinkers_query_count)
    
    # EXTERNAL SOFTWARE INTERLINKERS
    used_external_interlinkers_query = db.query(
            ExternalAsset.externalinterlinker_id,
        ).filter(
            ExternalAsset.externalinterlinker_id != None
        ).group_by(ExternalAsset.externalinterlinker_id)
    used_external_interlinkers_query_all = used_external_interlinkers_query.all()
    used_external_interlinkers_query_count = used_external_interlinkers_query.count()

    get_raw_query(used_external_interlinkers_query)
    add(data, "Used external interlinkers:", used_external_interlinkers_query_all)
    add(data, "Number of used external interlinkers:", used_external_interlinkers_query_count)

    # KNOWLEDGE
    used_knowledge_interlinkers_query = db.query(
            InternalAsset.knowledgeinterlinker_id,
        ).filter(
            InternalAsset.knowledgeinterlinker_id != None
        ).group_by(InternalAsset.knowledgeinterlinker_id)
    used_knowledge_interlinkers_query_all = used_knowledge_interlinkers_query.all()
    used_knowledge_interlinkers_query_count = used_knowledge_interlinkers_query.count()

    get_raw_query(used_knowledge_interlinkers_query)
    add(data, "Used knowledge interlinkers:", used_knowledge_interlinkers_query_all)
    add(data, "Number of used knowledge interlinkers:", used_knowledge_interlinkers_query_count)

    print(data)
    db.close()
    return data

if __name__ == "__main__":
    logger.info("Creating initial data")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    logger.info("Initial data created")
    

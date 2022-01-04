import json
import logging

import requests

from app import crud, schemas
from app.config import settings
from app.general.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()

    print("WAIT UNTIL ALL DEMO DATA IS CREATED")
    SCHEMA = crud.coproductionschema.create(
            db=db,
            coproductionschema=schemas.CoproductionSchemaCreate(
                name="MAIN_SCHEMA",
                description="desc",
                is_public=True
            )
        )
    
    with open('app/general/init_data/interlinkers.json') as json_file:
        interlinkers_data = json.load(json_file)
        
    with open('app/general/init_data/cleaned.json') as json_file:
        data = json.load(json_file)
    
    for phaseName in data["phases"]:
        phase = crud.phases.create(
            db=db,
            phase=schemas.PhaseCreate(
                name=phaseName,
                is_public=True,
                description="demo description"
            )
        )
        for objectiveName in data["phases"][phaseName]:
            if objectiveName:
                objective = crud.objective.create(
                    db=db,
                    objective=schemas.ObjectiveCreate(
                        name=objectiveName,
                        is_public=True,
                        description="demo description",
                        phase_id=phase.id
                    )
                )
                for taskName in data["phases"][phaseName][objectiveName]:
                    if taskName:
                        task = crud.task.create(
                            db=db,
                            task=schemas.TaskCreate(
                                name=taskName,
                                is_public=True,
                                description="demo description",
                                objective_id=objective.id
                            )
                        )

                        for interlinkerId in data["phases"][phaseName][objectiveName][taskName]:
                            for interlinker in interlinkers_data:
                                interlinkerName = interlinker["name"]
                                if interlinker["id"] == interlinkerId:
                                    response = requests.get(f"http://{settings.CATALOGUE_SERVICE}/api/v1/interlinkers/get_by_name/{interlinkerName}".replace(" ", "%20"))
                                    interlinker_data = response.json()
                                    crud.task.add_recommended_interlinker(
                                        db=db,
                                        task=task,
                                        interlinker_id=interlinker_data["id"]
                                    )
        crud.coproductionschema.add_phase(
            db=db,
            coproductionschema=SCHEMA,
            phase=phase
        )

    db.close()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

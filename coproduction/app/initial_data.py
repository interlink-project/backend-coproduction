import json
import logging
import os
from pathlib import Path

import requests

from app import crud, schemas
from app.config import settings
from app.general.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_SCHEMA_NAME = "Default schema"


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


def main() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()

    for schema_metadata_path in Path("/app/interlinkers-data/schemas").glob("**/metadata.json"):
        with open(str(schema_metadata_path)) as json_file:
            print(
                f"{bcolors.OKBLUE}## PROCESSING {bcolors.ENDC}{schema_metadata_path}{bcolors.OKBLUE}")
            parent = str(schema_metadata_path.parents[0])
            phases = os.listdir(parent + "/phases")
            schema_data = json.loads(json_file.read())

        schema_data["name_translations"] = schema_data["name"]
        schema_data["description_translations"] = schema_data["description"]
        SCHEMA = crud.coproductionschema.create(
            db=db,
            coproductionschema=schemas.CoproductionSchemaCreate(
                **schema_data
            )
        )

        for phase in phases:
            with open(parent + "/phases/" + phase) as json_file:
                phase_data = json.loads(json_file.read())
            phase_data["name_translations"] = phase_data["name"]
            phase_data["description_translations"] = phase_data["description"]
            phase_data["coproductionschema_id"] = SCHEMA.id

            db_phase = crud.phase.create(
                db=db,
                phase=schemas.PhaseCreate(
                    **phase_data
                )
            )

            for objective in phase_data["objectives"]:
                objective_data = objective
                objective_data["name_translations"] = objective["name"]
                objective_data["description_translations"] = objective["description"]
                objective_data["phase_id"] = db_phase.id

                db_objective = crud.objective.create(
                    db=db,
                    objective=schemas.ObjectiveCreate(
                        **objective_data
                    )
                )

                for task in objective_data["tasks"]:
                    task_data = task
                    task_data["name_translations"] = task_data["name"]
                    task_data["description_translations"] = task_data["description"]
                    task_data["objective_id"] = db_objective.id

                    db_task = crud.task.create(
                        db=db,
                        task=schemas.TaskCreate(
                            **task_data
                        )
                    )

    TEAM = crud.team.create(
        db=db,
        team=schemas.TeamCreate(
            name="Example team",
            description="Good team",
            logotype=""
        )
    )

    COPRODUCTION_PROCESS_NAME = "Example"
    crud.coproductionprocess.create(
        db=db,
        coproductionprocess=schemas.CoproductionProcessCreate(
            # artefact_id=interlinker.id,
            name=COPRODUCTION_PROCESS_NAME,
            logotype="/static/demodata/interlinkers/slack.png",
            description="This is a demo process 2",
            team_id=TEAM.id,
            coproductionschema_id=SCHEMA.id
        ),
    )
    print(f"\n{bcolors.OKGREEN}'{COPRODUCTION_PROCESS_NAME}' coproduction process created{bcolors.ENDC}")
    
    db.close()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

import logging
import requests

from app import crud, schemas
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

    if (sc := crud.coproductionschema.get_by_name(db=db, locale="en", name="Default schema")):
        crud.coproductionschema.remove(db=db, id=sc.id)
        print("Schema removed")

    data = requests.get("https://raw.githubusercontent.com/interlink-project/interlinkers-data/master/all.json").json()
    # with open("/app/interlinkers-data/all.json") as json_file:
    #     data = json.load(json_file)

    for schema_data in data["schemas"]:
        name = schema_data["name"]["en"]
        print(f"{bcolors.OKBLUE}## PROCESSING {bcolors.ENDC}{name}{bcolors.OKBLUE}")

        schema_data["name_translations"] = schema_data["name"]
        schema_data["description_translations"] = schema_data["description"]
        SCHEMA = crud.coproductionschema.create(
            db=db,
            coproductionschema=schemas.CoproductionSchemaCreate(
                **schema_data
            )
        )

        resume = {}
        for phase_data in schema_data["phases"]:
            phase_data["name_translations"] = phase_data["name"]
            phase_data["description_translations"] = phase_data["description"]
            phase_data["coproductionschema_id"] = SCHEMA.id

            db_phase = crud.phase.create(
                db=db,
                phase=schemas.PhaseCreate(
                    **phase_data
                )
            )
            resume[phase_data["reference"]] = {
                "id": db_phase.id,
                "prerequisites": phase_data["prerequisites"]
            }

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
                    sum = list(task_data["problem_profiles"]) + list(objective_data["problem_profiles"])
                    task_data["problem_profiles"] = list(set(sum))
                    print(task_data["problem_profiles"])                    
                    db_task = crud.task.create(
                        db=db,
                        task=schemas.TaskCreate(
                            **task_data
                        )
                    )
        
        print(resume)
        for key, phase_resume in resume.items():
            print(phase_resume)
            db_phase = crud.phase.get(db=db, id=phase_resume["id"])
            for prerequisite_reference in phase_resume["prerequisites"]:
                db_prerequisite = crud.phase.get(db=db, id=resume[prerequisite_reference]["id"])
                print("Adding", db_prerequisite, "to", db_phase)
                crud.phase.add_prerequisite(db=db, phase=db_phase, prerequisite=db_prerequisite)
    db.close()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

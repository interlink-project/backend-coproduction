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
    
    if (sc := crud.coproductionschema.get_by_name(db=db, locale="en", name="hackathon")):
        crud.coproductionschema.remove(db=db, id=sc.id)
        print("Schema removed")

    data = requests.get("https://raw.githubusercontent.com/interlink-project/interlinkers-data/master/all.json").json()
    # with open("/app/interlinkers-data/all.json") as json_file:
    #     data = json.load(json_file)

    for schema_data in data["schemas"]:
        name = schema_data["name_translations"]["en"]
        print(f"{bcolors.OKBLUE}## PROCESSING {bcolors.ENDC}{name}{bcolors.OKBLUE}")
        SCHEMA = crud.coproductionschema.create(
            db=db,
            coproductionschema=schemas.CoproductionSchemaCreate(
                **schema_data, is_public=True
            )
        )
        phases_resume = {}
        phase_data: dict
        for phase_data in schema_data["phases"]:
            phase_data["coproductionschema_id"] = SCHEMA.id

            db_phase = crud.phasemetadata.create(
                db=db,
                phasemetadata=schemas.PhaseMetadataCreate(
                    **phase_data
                )
            )
            phases_resume[phase_data["reference"]] = {
                "id": db_phase.id,
                "prerequisites": phase_data.get("prerequisites", [])
            }

            objectives_resume = {}
            objective_data : dict 
            for objective_data in phase_data["objectives"]:
                objective_data["phasemetadata_id"] = db_phase.id

                db_objective = crud.objectivemetadata.create(
                    db=db,
                    objectivemetadata=schemas.ObjectiveMetadataCreate(
                        **objective_data
                    )
                )
                objectives_resume[objective_data["reference"]] = {
                    "id": db_objective.id,
                    "prerequisites": objective_data.get("prerequisites", [])
                }

                tasks_resume = {}
                task_data : dict
                for task_data in objective_data["tasks"]:
                    task_data["objectivemetadata_id"] = db_objective.id
                    sum = list(task_data["problem_profiles"]) + list(objective_data["problem_profiles"])
                    task_data["problem_profiles"] = list(set(sum))
                    db_task = crud.taskmetadata.create(
                        db=db,
                        taskmetadata=schemas.TaskMetadataCreate(
                            **task_data
                        )
                    )
                    tasks_resume[task_data["reference"]] = {
                        "id": db_task.id,
                        "prerequisites": task_data.get("prerequisites", [])
                    }
                ## prerequisites
                for key, task_resume in tasks_resume.items():
                    db_taskmetadata = crud.taskmetadata.get(db=db, id=task_resume["id"])
                    prerequisite_reference: dict
                    for prerequisite_reference in task_resume["prerequisites"]:
                        if (ref := prerequisite_reference.get("item", None)):
                            db_prerequisite = crud.taskmetadata.get(db=db, id=tasks_resume[ref]["id"])
                            print(db_prerequisite, "is a prerequisite for", db_task)
                            crud.taskmetadata.add_prerequisite(db=db, taskmetadata=db_taskmetadata, prerequisite=db_prerequisite)
            for key, objective_resume in objectives_resume.items():
                db_objectivemetadata = crud.objectivemetadata.get(db=db, id=objective_resume["id"])
                prerequisite_reference: dict
                for prerequisite_reference in objective_resume["prerequisites"]:
                    if (ref := prerequisite_reference.get("item", None)):
                        db_prerequisite = crud.objectivemetadata.get(db=db, id=objectives_resume[ref]["id"])
                        print(db_prerequisite, "is a prerequisite for", db_objective)
                        crud.objectivemetadata.add_prerequisite(db=db, objectivemetadata=db_objectivemetadata, prerequisite=db_prerequisite)
        print(phases_resume)
        for key, phase_resume in phases_resume.items():
            db_phasemetadata = crud.phasemetadata.get(db=db, id=phase_resume["id"])
            for prerequisite_reference in phase_resume["prerequisites"]:
                if (ref := prerequisite_reference.get("item", None)):
                    db_prerequisite = crud.phasemetadata.get(db=db, id=phases_resume[ref]["id"])
                    print(db_prerequisite, "is a prerequisite for", db_phasemetadata)
                    crud.phasemetadata.add_prerequisite(db=db, phasemetadata=db_phasemetadata, prerequisite=db_prerequisite)
        db.close()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

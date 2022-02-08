import json
import logging

import requests

from app import crud, schemas
from app.config import settings
from app.general.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_SCHEMA_NAME = "default"

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

"""
{
    "name": "Skeleton to guide the description of the main aim of the collaborative project",
    "id": 1
},
"""
interlinkers = [
    {
        "name": "Google Drive",
        "id": 1
    }
]
data = {
    "phases": {
        "engage": {
            "identify_stakeholders": {
                "map_stakeholders_analyse_motivation_skills_expectations": [1],
                "visually_map_the_network_of_stakeholders": [1],
                "create_a_contact_list_of_potential_network_participants": [1]
            },
            "engage_stakeholders": {
                "prepare_an_engagement_plan": [1],
                "create_awareness_and_communication": [1],
                "communicate_benefit_for_stakeholders": [1],
                "engage_citizens_in_the_coproduction_process": [1]
            },
            "define_legal_and_ethical_framework": {
                "define_a_nondisclosure_agreement": [1],
                "define_a_partnership_agreement": [1]
            },
            "focus_the_problem_collaboratively": {
                "collaboratively_analyse_the_problem": [1],
                "gather_needs_and_ideas_via_crowdsourcing": [1],
                "sketch_an_initial_idea_of_the_service": [1],
                "collaborative_agree_on_a_service_idea": [1],
                "define_requirements_and_constraints_for_the_service": [1]
            },
            "define_data_management_plan": {
                "clarify_the_purpose_for_data_collection": [1],
                "understand_how_the_data_flows": [1],
                "be_aware_of_data_impact": [1],
                "to_be_completed_with_input_from_wp": [1]
            }
        },
        "design": {
            "problem_exploration": {
                "ideas_collection_for_problem_refinement": [1],
                "ideas_crowdsourcing": [1],
                "context_analysis": [1],
                "map_of_actors": [1],
                "collect_data": [1]
            },
            "service_design": {
                "define_personas": [1],
                "define_scenarios": [1],
                "define_user_journeys": [1],
                "engage_relevant_actors_in_the_design": [1],
                "prototype": [1]
            },
            "service_specification": {
                "service_specification": [1],
                "user_interface_design": [1],
                "data_model_design": [1],
                "software_architecture_and_api_design": [1]
            },
            "sustainability": {
                "evaluation_of_codesign": [1],
                "refine_the_preliminary_business_model": [1]
            }
        },
        "build": {
            "technical_implementation": {
                "some task": [1]
            },
            "service_implementation": {
                "another task": [1]
            },
            "service_codelivery": {
                "identify_all_the_actors_engaged_in_the_codelivery_their_role_and_responsability": [1],
                "coordinate_the_actors_involved_in_the_codelivery_of_the_service": [1],
                "guarantee_transparent_communication_about_the_service_codelivered": [1]
            }
        },
        "sustain": {
            "handover": {
                "one task": [1]
            },
            "maintenance": {
                "task_distribution_for_maintenancecontracts_regulationdata_management_archiving": [1]
            },
            "coevaluation": {
                "monitoring_ongoing_evaluationperiodic_evaluations_with_stakeholders": [1]
            }
        }
    }
}

import os
from pathlib import Path

def main() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()

    for schema_metadata_path in Path("/app/interlinkers-data/schemas").glob("**/metadata.json"):
        with open(str(schema_metadata_path)) as json_file:
            print(f"{bcolors.OKBLUE}## PROCESSING {bcolors.ENDC}{schema_metadata_path}{bcolors.OKBLUE}")
            parent = str(schema_metadata_path.parents[0])
            phases = os.listdir(parent + "/phases")
            schema_data = json.loads(json_file.read())
        
        schema_data["is_public"] = True
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
            print(phase_data)
            """phase = crud.phases.create(
                db=db,
                phase=schemas.PhaseCreate(
                    name=phaseName,
                    is_public=True,
                    description="demo description"
                )
            )"""


    """
    

    for phaseName in data["phases"]:
        
        print(f"\n{bcolors.WARNING}PHASE: {phaseName}{bcolors.ENDC}")
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
                print(f"  {bcolors.OKCYAN}OBJECTIVE: {objectiveName}{bcolors.ENDC}")
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
                        print(f"    {bcolors.HEADER}TASK: {taskName}{bcolors.ENDC}")

                        for interlinkerId in data["phases"][phaseName][objectiveName][taskName]:
                            for interlinker in interlinkers:
                                interlinkerName = interlinker["name"]
                                if interlinker["id"] == interlinkerId:
                                    response = requests.get(
                                        f"http://{settings.CATALOGUE_SERVICE}/api/v1/interlinkers/get_by_name/{interlinkerName}".replace(" ", "%20"))
                                    if response.status_code != 200:
                                        print(f"      {bcolors.FAIL}INTERLINKER: '{interlinkerName}' named interlinker is not accessible")

        print(f"{bcolors.OKGREEN}'{phaseName}' phase successfully added to '{DEFAULT_SCHEMA_NAME}' schema{bcolors.ENDC}")
        crud.coproductionschema.add_phase(
            db=db,
            coproductionschema=SCHEMA,
            phase=phase
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
            schema_id=SCHEMA.id
        ),
    )
    print(f"\n{bcolors.OKGREEN}'{COPRODUCTION_PROCESS_NAME}' coproduction process created{bcolors.ENDC}")
    """
    db.close()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

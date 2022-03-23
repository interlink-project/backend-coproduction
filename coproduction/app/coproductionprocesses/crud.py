from cmath import phase
import uuid
from typing import Any, Dict, Optional, List

import requests
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from app import crud, schemas
from app.config import settings
from app.general.utils.CRUDBase import CRUDBase
from app.models import CoproductionProcess, CoproductionSchema, Team
from app.schemas import CoproductionProcessCreate, CoproductionProcessPatch
from app.initial_data import DEFAULT_SCHEMA_NAME
from app.memberships.models import Membership
from app import models, schemas
from slugify import slugify
from app.coproductionschemas.crud import exportCrud as schemas_crud

from slugify import slugify

class CRUDCoproductionProcess(CRUDBase[CoproductionProcess, CoproductionProcessCreate, CoproductionProcessPatch]):
    def get_by_name(self, db: Session, name: str) -> Optional[Team]:
        return db.query(CoproductionProcess).filter(CoproductionProcess.name == name).first()

    def get_by_artefact(self, db: Session, artefact_id: uuid.UUID) -> Optional[CoproductionProcess]:
        return db.query(CoproductionProcess).filter(CoproductionProcess.artefact_id == artefact_id).first()

    def get_multi_by_user(self, db: Session, user_id: str) -> Optional[List[CoproductionProcess]]:
        return db.query(
            CoproductionProcess
        ).join(
            CoproductionProcess.teams
        ).filter(
            Team.id == Membership.team_id,
        ).filter(
            Membership.user_id == user_id,
        ).all()


    def add_team(self, db: Session, coproductionprocess: CoproductionProcess, team: models.Team):
        coproductionprocess.teams.append(team)
        db.commit()
        db.refresh(coproductionprocess)
        return coproductionprocess
        
    def create(self, db: Session, *, coproductionprocess: CoproductionProcessCreate, creator: models.User) -> CoproductionProcess:
        team = crud.team.get(db=db, id=coproductionprocess.team_id)
        db_obj = CoproductionProcess(
            artefact_id=coproductionprocess.artefact_id,
            # uses postgres
            name=coproductionprocess.name,
            description=coproductionprocess.description,
            aim=coproductionprocess.aim,
            idea=coproductionprocess.idea,
            organization=coproductionprocess.organization,
            challenges=coproductionprocess.challenges,
            # relations
            creator=creator,
        )
        db_obj.teams.append(team)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        crud.acl.create(db=db, coproductionprocess=db_obj)
        db.refresh(db_obj)
        return db_obj

    def set_schema(self, db: Session, coproductionprocess: models.CoproductionProcess, coproductionschema: models.CoproductionSchema, language: str = "en"):
        if coproductionschema and hasattr(coproductionschema, "phasemetadatas"):
            total = {}
            for phasemetadata in coproductionschema.phasemetadatas:
                db_phase = crud.phase.create_from_metadata(
                    db=db,
                    phasemetadata=phasemetadata,
                    coproductionprocess_id=coproductionprocess.id,
                    language=language
                )

                ## Add new phase object and the prerequisites for later loop
                name = phasemetadata.name_translations[language]
                total_key = "phase-" + slugify(name)
                total[total_key] = {
                    "prerequisites": ["phase-" + slugify(prereq.name) for prereq in phasemetadata.prerequisites],
                    "newObj": db_phase,
                }
                
                if hasattr(phasemetadata, "objectivemetadatas") and phasemetadata.objectivemetadatas:
                    for objectivemetadata in phasemetadata.objectivemetadatas:
                        db_obj = crud.objective.create_from_metadata(
                            db=db,
                            objectivemetadata=objectivemetadata,
                            phase_id=db_phase.id,
                            language=language
                        )

                        ## Add new objective object and the prerequisites for later loop
                        name = objectivemetadata.name_translations[language]
                        total_key = "objective-" + slugify(name)
                        total[total_key] = {
                            "prerequisites": ["objective-" + slugify(prereq.name) for prereq in objectivemetadata.prerequisites],
                            "newObj": db_obj,
                        }

                        if hasattr(objectivemetadata, "taskmetadatas") and objectivemetadata.taskmetadatas:
                            for taskmetadata in objectivemetadata.taskmetadatas:
                                db_task = crud.task.create_from_metadata(
                                    db=db,
                                    taskmetadata=taskmetadata,
                                    objective_id=db_obj.id,
                                    language=language
                                )
                                ## Add new task object and the prerequisites for later loop
                                name = taskmetadata.name_translations[language]
                                total_key = "task-" + slugify(name)
                                total[total_key] = {
                                    "prerequisites": ["task-" + slugify(prereq.name) for prereq in taskmetadata.prerequisites],
                                    "newObj": db_task,
                                }
                        else:
                            print("OBJECTIVE HAS NO TASKS")
                else:
                    print("PHASE HAS NO OBJECTIVES")

            print(total)
            # iterate over phases to poblate with prerequisites using total dict
            for new_phase in coproductionprocess.phases:
                entry = total["phase-" + slugify(new_phase.name)]
                for prerequisite_name in entry["prerequisites"]:
                    prerequisite = total[prerequisite_name]["newObj"]
                    crud.phase.add_prerequisite(db=db, phase=new_phase, prerequisite=prerequisite)

                # objectives
                for new_objective in new_phase.objectives:
                    entry = total["objective-" + slugify(new_objective.name)]
                    for prerequisite_name in entry["prerequisites"]:
                        prerequisite = total[prerequisite_name]["newObj"]
                        crud.objective.add_prerequisite(db=db, objective=new_objective, prerequisite=prerequisite)

                    # objectives
                    for new_task in new_objective.tasks:
                        entry = total["task-" + slugify(new_task.name)]
                        for prerequisite_name in entry["prerequisites"]:
                            prerequisite = total[prerequisite_name]["newObj"]
                            crud.task.add_prerequisite(db=db, task=new_task, prerequisite=prerequisite)
        else:
            print("SCHEMA HAS NO PHASES")

        return coproductionprocess

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


exportCrud = CRUDCoproductionProcess(CoproductionProcess)

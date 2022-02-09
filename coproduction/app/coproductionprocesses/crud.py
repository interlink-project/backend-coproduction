import uuid
from typing import Any, Dict, Optional, Union

import requests
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from app import crud, schemas
from app.config import settings
from app.general.utils.CRUDBase import CRUDBase
from app.models import CoproductionProcess, CoproductionSchema, Team
from app.schemas import CoproductionProcessCreate, CoproductionProcessPatch
from app.extern import acl
from app.schemas import RoleCreate, RolePatch
from app.initial_data import DEFAULT_SCHEMA_NAME
from app.memberships.models import Membership

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)

    return d

class CRUDCoproductionProcess(CRUDBase[CoproductionProcess, CoproductionProcessCreate, CoproductionProcessPatch]):
    def get_by_name(self, db: Session, name: str) -> Optional[Team]:
        return db.query(CoproductionProcess).filter(CoproductionProcess.name == name).first()
        
    def get_by_artefact(self, db: Session, artefact_id: uuid.UUID) -> Optional[CoproductionProcess]:
        return db.query(CoproductionProcess).filter(CoproductionProcess.artefact_id == artefact_id).first()

    def get_multi_by_user(self, db: Session, user_id: str) -> Optional[Team]:
        return db.query(
            CoproductionProcess
        ).filter(
            CoproductionProcess.team_id == Team.id,
        ).filter(
            Team.id == Membership.team_id,
        ).filter(
            Membership.user_id == user_id,
        ).all()

    def create(self, db: Session, *, coproductionprocess: CoproductionProcessCreate, creator: dict) -> CoproductionProcess:
        aclobj = acl.create_acl()

        team = crud.team.get(db=db, id=coproductionprocess.team_id)
        coproductionschema = crud.coproductionschema.get(db=db, id=coproductionprocess.coproductionschema_id) or crud.coproductionschema.get_by_name(db=db, name=DEFAULT_SCHEMA_NAME, locale="en")
        db_obj = CoproductionProcess(
            artefact_id=coproductionprocess.artefact_id,
            # uses postgres
            name=coproductionprocess.name,
            description=coproductionprocess.description,
            aim=coproductionprocess.aim,
            idea=coproductionprocess.idea,
            organization=coproductionprocess.organization,
            challenges=coproductionprocess.challenges,
            #relations
            created_by=creator["sub"],
            team=team,
            coproductionschema=coproductionschema,
            # uses mongo
            acl_id=aclobj["_id"]
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Create all roles
        for membership in team.memberships:
            role = RoleCreate(**{
                "role": "admin",
                "type": "team_member",
                "coproductionprocess_id": db_obj.id,
                "user_id": membership.user_id,
            })
            crud.role.create(db=db, role=role)

        # Copy the tree of the schema
        if coproductionschema and hasattr(coproductionschema, "phases"):
            for phase in coproductionschema.phases:
                print(phase)
                clone = row2dict(phase)
                clone["coproductionprocess_id"] = db_obj.id
                clone["parent_id"] = phase.id
                del clone["coproductionschema_id"]
                del clone["created_at"]
                del clone["updated_at"]
                db_phase = crud.phase.create(
                    db=db,
                    phase=schemas.PhaseCreate(**clone)
                )
                if hasattr(phase, "objectives") and phase.objectives:
                    for objective in phase.objectives:
                        clone = row2dict(objective)
                        clone["phase_id"] = db_phase.id
                        clone["parent_id"] = objective.id
                        del clone["created_at"]
                        del clone["updated_at"]
                        print(objective)
                        db_objective = crud.objective.create(
                            db=db,
                            objective=schemas.ObjectiveCreate(**clone)
                        )
                        if hasattr(objective, "tasks") and objective.tasks:
                            for task in objective.tasks:
                                clone = row2dict(task)
                                clone["objective_id"] = db_objective.id
                                clone["parent_id"] = task.id
                                del clone["created_at"]
                                del clone["updated_at"]
                                print(task)
                                db_task = crud.task.create(
                                    db=db,
                                    task=schemas.TaskCreate(**clone)
                                )
                        else:
                            print("OBJECTIVE HAS NO TASKS")
                else:
                    print("PHASE HAS NO OBJECTIVES")
        else:
            print("SCHEMA HAS NO PHASES")

        db.refresh(db_obj)
        return db_obj

    # CRUD Permissions
    def can_create(self, user):
        return True

    def can_list(self, user):
        return True

    def check_perm(self, db: Session, user, object, perm):
        role = crud.role.get_user_role_for_process(db=db, user_id=user["email"], coproductionprocess_id=object.id)
        if not role:
            role = "anonymous"
        else:
            role = role.role
            # raise HTTPException(status_code=403, detail="Role do not exist")
        return True
        return acl.check_permissions_for_action(object.acl_id, perm, role)

    def can_read(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="retrieve")

    def can_update(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="update")

    def can_remove(self, db: Session, user, object):
        return self.check_perm(db=db, user=user, object=object, perm="delete")


exportCrud = CRUDCoproductionProcess(CoproductionProcess)

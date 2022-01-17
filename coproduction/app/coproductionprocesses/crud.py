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

class CRUDCoproductionProcess(CRUDBase[CoproductionProcess, CoproductionProcessCreate, CoproductionProcessPatch]):
    def get_by_artefact(self, db: Session, artefact_id: uuid.UUID) -> Optional[CoproductionProcess]:
        return db.query(CoproductionProcess).filter(CoproductionProcess.artefact_id == artefact_id).first()

    def create(self, db: Session, *, coproductionprocess: CoproductionProcessCreate) -> CoproductionProcess:
        aclobj = acl.create_acl()

        team = crud.team.get(db=db, id=coproductionprocess.team_id)
        schema = crud.coproductionschema.get(db=db, id=coproductionprocess.schema_id)
        db_obj = CoproductionProcess(
            artefact_id=coproductionprocess.artefact_id,
            # uses postgres
            name=coproductionprocess.name,
            logotype=coproductionprocess.logotype,
            description=coproductionprocess.description,
            aim=coproductionprocess.aim,
            idea=coproductionprocess.idea,
            organization=coproductionprocess.organization,
            challenges=coproductionprocess.challenges,
            #relations
            team=team,
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

        # Create all phaseinstantiations
        if not schema:
            schema = crud.coproductionschema.get_by_name(db=db, name="MAIN_SCHEMA")
        if hasattr(schema, "phases"):
            for ph in schema.phases:
                crud.phaseinstantiation.create(
                    db=db,
                    phaseinstantiation=schemas.PhaseInstantiationCreate(
                        coproductionprocess_id=db_obj.id,
                        phase_id=ph.id
                    )
                )
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

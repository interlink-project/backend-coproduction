from typing import Any, List, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.api_v1 import (
    assets,
    coproductionprocesses,
    coproductionschemas,
    objectives,
    phases,
    tasks,
    teams,
    users,
    roles
)
from app.config import settings
from app.general import deps

api_router = APIRouter()
@api_router.get("/me", response_model=schemas.UserOutFull)
def list_assets(
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    return current_user

api_router.include_router(coproductionschemas.router,
                          prefix="/coproductionschemas", tags=["coproductionschemas"])

api_router.include_router(coproductionprocesses.router,
                          prefix="/coproductionprocesses", tags=["coproductionprocesses"])

api_router.include_router(phases.router,
                          prefix="/phases", tags=["tree"])
api_router.include_router(objectives.router,
                          prefix="/objectives", tags=["tree"])
api_router.include_router(tasks.router,
                          prefix="/tasks", tags=["tree"])
api_router.include_router(assets.router,
                          prefix="/assets", tags=["tree"])

api_router.include_router(teams.router,
                          prefix="/teams", tags=["teammanagement"])

api_router.include_router(roles.router,
                          prefix="/roles", tags=["teammanagement"])
api_router.include_router(users.router,
                          prefix="/users", tags=["teammanagement"])

@api_router.get("/")
def main():
    return RedirectResponse(url="/api/v1/coproductionprocesses")

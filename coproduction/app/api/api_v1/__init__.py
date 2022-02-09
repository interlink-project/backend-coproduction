from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.api.api_v1 import (
    coproductionschemas,
    coproductionprocesses, 
    phases, 
    tasks, 
    objectives, 
    assets,
    teams,
    memberships
)


api_router = APIRouter()
api_router.include_router(coproductionschemas.router,
                          prefix="/coproductionschemas", tags=["coproductionschemas"])

api_router.include_router(coproductionprocesses.router,
                          prefix="/coproductionprocesses", tags=["coproductionprocesses"])
# api_router.include_router(phases.router,
#                           prefix="/phases", tags=["coproduction"])
api_router.include_router(objectives.router,
                          prefix="/objectives", tags=["tree"])
api_router.include_router(tasks.router,
                          prefix="/tasks", tags=["tree"])
api_router.include_router(assets.router,
                          prefix="/assets", tags=["assets"])

team_management_router = APIRouter()
team_management_router.include_router(teams.router,
                          prefix="/teams", tags=["teammanagement"])

team_management_router.include_router(memberships.router,
                          prefix="/memberships", tags=["teammanagement"])

@api_router.get("/")
def main():
    return RedirectResponse(url="/api/v1/coproductionprocesses")

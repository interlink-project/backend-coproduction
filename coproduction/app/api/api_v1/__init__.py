from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.api.api_v1 import (
    coproductionschemas,
    coproductionprocesses, 
    phaseinstantiations, 
    taskinstantiations, 
    objectiveinstantiations, 
    assets,
    teams,
    memberships
)


api_router = APIRouter()
api_router.include_router(coproductionschemas.router,
                          prefix="/coproductionschemas", tags=["coproduction"])

api_router.include_router(coproductionprocesses.router,
                          prefix="/coproductionprocesses", tags=["coproduction"])
api_router.include_router(phaseinstantiations.router,
                          prefix="/phaseinstantiations", tags=["coproduction"])
api_router.include_router(objectiveinstantiations.router,
                          prefix="/objectiveinstantiations", tags=["coproduction"])
api_router.include_router(taskinstantiations.router,
                          prefix="/taskinstantiations", tags=["coproduction"])
api_router.include_router(assets.router,
                          prefix="/assets", tags=["coproduction"])

team_management_router = APIRouter()
team_management_router.include_router(teams.router,
                          prefix="/teams", tags=["teammanagement"])

team_management_router.include_router(memberships.router,
                          prefix="/memberships", tags=["teammanagement"])

@api_router.get("/")
def main():
    return RedirectResponse(url="/api/v1/coproductionprocesses")

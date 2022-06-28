from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.api.api_v1 import (
    assets,
    coproductionprocesses,
    objectives,
    phases,
    tasks,
    teams,
    users,
    permissions,
    organizations
)

api_router = APIRouter()

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
api_router.include_router(permissions.router,
                          prefix="/permissions", tags=["teammanagement"])
api_router.include_router(users.router,
                          prefix="/users", tags=["teammanagement"])
api_router.include_router(organizations.router,
                          prefix="/organizations", tags=["teammanagement"])


@api_router.get("/")
async def main():
    return RedirectResponse(url="/api/v1/coproductionprocesses")

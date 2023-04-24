import uuid
from typing import Any, List, Optional

import requests
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from app.messages import log
from app.assets.schemas import *
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings
from app.general import deps

from app.recomenders import recomender_type_governance

router = APIRouter()


class CustomForm(BaseModel):
    SampleData: List[str]
    TrainingData: List[Dict[str, str]]



@router.post("/typegovernancemodel")
async def recomendTypeGovernance(
    form_data: CustomForm,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:

    return recomender_type_governance( form_data.TrainingData,form_data.SampleData)

    
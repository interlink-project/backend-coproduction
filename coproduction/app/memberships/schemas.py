import uuid
from typing import Optional

from pydantic import BaseModel, root_validator
from app.general.utils.AllOptional import AllOptional
from datetime import datetime
import requests
from app.config import settings

class MembershipBase(BaseModel):
    user_id: str


class MembershipCreate(MembershipBase):
    team_id: uuid.UUID


class MembershipPatch(MembershipBase, metaclass=AllOptional):
    pass


class Membership(MembershipBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class MembershipOut(Membership):
    picture: Optional[str]
    email: Optional[str]
    
    @root_validator(pre=True)
    def get_user_data_from_auth_microservice(cls, values):
        id = values["user_id"]
        try:
            newValues = {**values}
            response = requests.get(f"http://{settings.AUTH_SERVICE}/auth/api/v1/users/{id}").json()
            newValues["picture"] = response["picture"]
            newValues["email"] = response["email"]
            return newValues
        except:
            return values
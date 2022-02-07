import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
import os

class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROTOCOL: str
    SERVER_NAME: str
    BASE_PATH: str
    COMPLETE_SERVER_NAME: AnyHttpUrl = os.getenv("PROTOCOL") + os.getenv("SERVER_NAME") + os.getenv("BASE_PATH")
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME = "Coproduction API"

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # OTHER MICROS
    ACL_SERVICE_NAME: str
    ACL_PORT: int
    ACL_SERVICE: str = os.getenv("ACL_SERVICE_NAME") + ":" + os.getenv("ACL_PORT")

    CATALOGUE_SERVICE_NAME: str
    CATALOGUE_PORT: int
    CATALOGUE_SERVICE: str = os.getenv("CATALOGUE_SERVICE_NAME") + ":" + os.getenv("CATALOGUE_PORT")

    class Config:
        case_sensitive = True

settings = Settings()

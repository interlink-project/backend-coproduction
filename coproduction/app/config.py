import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
import os

class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SENTRY_DSN: Optional[HttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

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

    CLIENT_ID: str
    CLIENT_SECRET: str
    SERVER_METADATA_URL: str

    # OTHER MICROS
    
    AUTH_SERVICE_NAME: str
    AUTH_PORT: int
    AUTH_SERVICE: str = os.getenv("AUTH_SERVICE_NAME") + ":" + os.getenv("AUTH_PORT")

    ACL_SERVICE_NAME: str
    ACL_PORT: int
    ACL_SERVICE: str = os.getenv("ACL_SERVICE_NAME") + ":" + os.getenv("ACL_PORT")

    TEAMMANAGEMENT_SERVICE_NAME: str
    TEAMMANAGEMENT_PORT: int
    TEAMMANAGEMENT_SERVICE: str = os.getenv("TEAMMANAGEMENT_SERVICE_NAME") + ":" + os.getenv("TEAMMANAGEMENT_PORT")
    
    CATALOGUE_SERVICE_NAME: str
    CATALOGUE_PORT: int
    CATALOGUE_SERVICE: str = os.getenv("CATALOGUE_SERVICE_NAME") + ":" + os.getenv("CATALOGUE_PORT")

    # file backend interlinkers

    GOOGLEDRIVE_SERVICE_NAME: str
    GOOGLEDRIVE_PORT: int
    GOOGLEDRIVE_SERVICE: str = os.getenv("GOOGLEDRIVE_SERVICE_NAME") + ":" + os.getenv("GOOGLEDRIVE_PORT")

    FILEMANAGER_SERVICE_NAME: str
    FILEMANAGER_PORT: int
    FILEMANAGER_SERVICE: str = os.getenv("FILEMANAGER_SERVICE_NAME") + ":" + os.getenv("FILEMANAGER_PORT")

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME = "Coproduction API"
    BASE_PATH: str

    class Config:
        case_sensitive = True

settings = Settings()

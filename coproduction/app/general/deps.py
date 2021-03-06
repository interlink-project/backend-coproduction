from typing import Generator, Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.general.db.session import SessionLocal
from app import crud, models
from starlette_context import context


def get_token_in_cookie(request):
    try:
        return request.cookies.get("auth_token")
    except:
        return None


def get_token_in_header(request):
    try:
        return request.headers.get('authorization').replace("Bearer ", "")
    except:
        return None


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_token(
    request: Request
) -> dict:
    return get_token_in_cookie(request) or get_token_in_header(request)


def get_current_active_token(
    current_token: str = Depends(get_current_token)
) -> dict:
    if not current_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return current_token


async def get_current_user(
    # request: Request,
    db: Session = Depends(get_db),
    # current_token: str = Depends(get_current_token)
) -> Optional[models.User]:
    try:
        if user := context.data.get("user", None):
            return await crud.user.get(db=db, id=user["sub"])
        return None
    except Exception as e:
        print(str(e))
        return None


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    # calls get_current_user, and if nothing is returned, raises Not authenticated exception
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return current_user

def get_current_active_superuser(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    # calls get_current_user, and if nothing is returned, raises Not authenticated exception
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not superuser")
    return current_user


def get_current_user_from_context(
    db: Session
):
    try:
        if user := context.data.get("user", None):
            return db.query(
                models.User
            ).filter(
                models.User.id == user["sub"]
            ).first()
        return

    except Exception as e:
        print(str(e))
        return None

from lib2to3.pgen2.token import OP
from typing import Generator, Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.general.db.session import SessionLocal
from app.general.authentication import decode_token
from app import crud, models

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
        state = request.state._state
        return state["token"]

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    try:
        token = get_token_in_cookie(request) or get_token_in_header(request)
        if token:
            token_data = decode_token(token)
            return crud.user.get_or_create(db=db, token_data=token_data)
        return None
    except Exception as e:
        print(str(e))
        return None

def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> models.User:
    # calls get_current_user, and if nothing is returned, raises Not authenticated exception
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return current_user
from typing import Generator

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.general.db.session import SessionLocal
from app.general.authentication import decode_token

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
) -> dict:
    try:
        token = get_token_in_cookie(request) or get_token_in_header(request)
        # gets user_data from state (see AuthMiddleware)
        if token:
            user_data = decode_token(token)
            return user_data
        return None
    except Exception as e:
        print(str(e))
        return None

def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    # calls get_current_user, and if nothing is returned, raises Not authenticated exception
    if current_user:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return current_user


def get_current_active_superuser(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if True:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

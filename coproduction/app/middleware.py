from contextvars import ContextVar
from fastapi import Depends
import json
from sqlalchemy_utils import TranslationHybrid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
import gettext
import enum
from app import models
from app.general import deps
from app.general.authentication import decode_token

class Locales(enum.Enum):
    en = "en"
    es = "es"
    it = "it"
    lv = "lv"

DEFAULT_LANGUAGE = Locales.en.value
SUPPORTED_LANGUAGE_CODES = [e.value for e in Locales]

_lang: ContextVar[str] = ContextVar("language", default=DEFAULT_LANGUAGE)


# def _(message: str) -> str:
#     return gettext.translation(
#         "base", localedir="locales", languages=[get_language()]
#     ).gettext(message)
    
def set_language(code) -> str:
    if code in SUPPORTED_LANGUAGE_CODES:
        _lang.set(code)
    else:
        raise Exception(f"{code} not in supported languages")

_user: ContextVar[str] = ContextVar("user", default=None)

def get_language() -> str:
    return _lang.get()

def set_user(token) -> str:
    try:
        _user.set(json.dumps(decode_token(token)))
    except:
        pass

def get_user() -> str:
    user_data = _user.get()
    return json.loads(user_data) if user_data and "sub" in user_data else None

def get_user_id() -> str:
    us = get_user()
    return us["sub"] if us else None

translation_hybrid = TranslationHybrid(
    current_locale=get_language,
    default_locale=DEFAULT_LANGUAGE
)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ):
        try:
            set_user(deps.get_current_token(request=request))
        except:
            pass

        try:
            header_lang = request.headers.get("accept-language")
            used_language = header_lang if header_lang in SUPPORTED_LANGUAGE_CODES else DEFAULT_LANGUAGE
            print("LANGUAGE", header_lang, used_language)
        except:
            used_language = DEFAULT_LANGUAGE

        language = _lang.set(used_language)
        response = await call_next(request)
        _lang.reset(language)
        return response

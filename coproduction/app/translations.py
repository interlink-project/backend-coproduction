from contextvars import ContextVar

from sqlalchemy_utils import TranslationHybrid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
import gettext
import enum

class Locales(enum.Enum):
    en = "en"
    es = "es"
    it = "it"

DEFAULT_LANGUAGE = Locales.en.value
SUPPORTED_LANGUAGE_CODES = [e.value for e in Locales]

_lang: ContextVar[str] = ContextVar(DEFAULT_LANGUAGE, default=None)


# def _(message: str) -> str:
#     return gettext.translation(
#         "base", localedir="locales", languages=[get_language()]
#     ).gettext(message)
    
def set_language(code) -> str:
    if code in SUPPORTED_LANGUAGE_CODES:
        _lang.set(code)
    else:
        raise Exception(f"{code} not in supported languages")

def get_language() -> str:
    return _lang.get()

translation_hybrid = TranslationHybrid(
    current_locale=get_language,
    default_locale=DEFAULT_LANGUAGE
)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
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

from contextvars import ContextVar

from sqlalchemy_utils import TranslationHybrid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

POSSIBLE_LOCALES = ["en", "eu", "es"]
DEFAULT_LOCALE = "en"

_lang: ContextVar[str] = ContextVar(DEFAULT_LOCALE, default=None)


def get_language() -> str:
    return _lang.get()


translation_hybrid = TranslationHybrid(
    current_locale=get_language,
    default_locale=DEFAULT_LOCALE
)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        try:
            lang = request.headers["accept-language"]
            print(lang)
            user_language = lang if lang in POSSIBLE_LOCALES else DEFAULT_LOCALE
        except:
            user_language = DEFAULT_LOCALE
        language = _lang.set(user_language)

        response = await call_next(request)

        _lang.reset(language)

        return response

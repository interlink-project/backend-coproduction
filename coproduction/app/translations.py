from contextvars import ContextVar

from sqlalchemy_utils import TranslationHybrid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

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
        
        user_language = request.headers["accept-language"].split(",")[1].split(";")[0]
        user_language = "en"
        language = _lang.set(user_language)

        response = await call_next(request)

        _lang.reset(language)

        return response

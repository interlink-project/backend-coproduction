from contextvars import ContextVar

from sqlalchemy_utils import TranslationHybrid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
import gettext


DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGE = ["es", "en"]

_lang: ContextVar[str] = ContextVar(DEFAULT_LANGUAGE, default=None)


def _(message: str) -> str:
    return gettext.translation(
        "base", localedir="locales", languages=[get_language()]
    ).gettext(message)
    

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

            lang = request.headers.get("accept-language")
            print("LANGUAGE")
            print(lang)

            # print(request.headers)
            user_language = lang if lang in SUPPORTED_LANGUAGE else DEFAULT_LANGUAGE
        except:
            user_language = DEFAULT_LANGUAGE

        language = _lang.set(user_language)

        response = await call_next(request)

        _lang.reset(language)

        return response

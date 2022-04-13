from contextvars import ContextVar
from sqlalchemy_utils import TranslationHybrid
import enum
from starlette_context import context

class Locales(enum.Enum):
    en = "en"
    es = "es"
    it = "it"
    lv = "lv"

DEFAULT_LANGUAGE_ENUM = Locales.en
DEFAULT_LANGUAGE = DEFAULT_LANGUAGE_ENUM.value
SUPPORTED_LANGUAGE_CODES = [e.value for e in Locales]

def get_language():
    return context.data.get("language", DEFAULT_LANGUAGE)


translation_hybrid = TranslationHybrid(
    current_locale=get_language,
    default_locale=DEFAULT_LANGUAGE
)
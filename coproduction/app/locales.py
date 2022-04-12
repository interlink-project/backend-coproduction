from contextvars import ContextVar
from sqlalchemy_utils import TranslationHybrid
import enum

class Locales(enum.Enum):
    en = "en"
    es = "es"
    it = "it"
    lv = "lv"

DEFAULT_LANGUAGE_ENUM = Locales.en
DEFAULT_LANGUAGE = DEFAULT_LANGUAGE_ENUM.value
SUPPORTED_LANGUAGE_CODES = [e.value for e in Locales]

_lang: ContextVar[str] = ContextVar("language", default=DEFAULT_LANGUAGE)

    
def set_language(code) -> str:
    if code in SUPPORTED_LANGUAGE_CODES:
        return _lang.set(code)
    else:
        raise Exception(f"{code} not in supported languages")

def reset_language(language) -> str:
    _lang.reset(language)


def get_language() -> str:
    return _lang.get()

translation_hybrid = TranslationHybrid(
    current_locale=get_language,
    default_locale=DEFAULT_LANGUAGE
)
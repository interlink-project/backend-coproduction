from sqlalchemy_utils import TranslationHybrid
from starlette_context import context
from app.config import settings

def get_language():
    try:
        return context.data.get("language", settings.DEFAULT_LANGUAGE)
    except:
        return settings.DEFAULT_LANGUAGE

translation_hybrid = TranslationHybrid(
    current_locale=get_language,
    default_locale=settings.DEFAULT_LANGUAGE
)
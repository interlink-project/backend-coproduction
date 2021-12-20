
from sqlalchemy_utils import TranslationHybrid


# For testing purposes we define this as simple function which returns
# locale 'fi'. Usually you would define this function as something that
# returns the user's current locale.
def get_locale():
    return 'es'


translation_hybrid = TranslationHybrid(
    current_locale=get_locale,
    default_locale='en'
)
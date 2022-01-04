import requests
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_team(team_id: str):
    logger.debug(f"Call to an external service: http://{settings.TEAMMANAGEMENT_SERVICE}/api/v1/teams/{team_id}/")
    response = requests.get(f"http://{settings.TEAMMANAGEMENT_SERVICE}/api/v1/teams/{team_id}/")
    return response.json()
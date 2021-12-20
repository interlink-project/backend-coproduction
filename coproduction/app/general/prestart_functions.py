import json
import logging

import requests
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.general.db.session import SessionLocal
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 10


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def waitForDatabase() -> None:
    try:
        db = SessionLocal()
        # Try to create session to check if DB is awake
        db.execute("SELECT 1")
    except Exception as e:
        logger.error(e)
        raise e

@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def waitForService(service) -> None:
    try:
        response = requests.get(f"http://{service}/healthcheck/")
        data = response.json()
    except Exception as e:
        raise e


def waitForGoogledrive() -> None:
    logger.info("Wait for google drive")
    logger.info(settings.GOOGLEDRIVE_SERVICE)
    waitForService(settings.GOOGLEDRIVE_SERVICE)

def waitForFilemanager() -> None:
    logger.info("Wait for file manager")
    logger.info(settings.FILEMANAGER_SERVICE)
    waitForService(settings.FILEMANAGER_SERVICE)

def waitForCatalogue() -> None:
    logger.info("Wait for catalogue")
    logger.info(settings.CATALOGUE_SERVICE)
    waitForService(settings.CATALOGUE_SERVICE)

def waitForTeammanagement() -> None:
    logger.info("Wait for teammanagement")
    logger.info(settings.TEAMMANAGEMENT_SERVICE)
    waitForService(settings.TEAMMANAGEMENT_SERVICE)
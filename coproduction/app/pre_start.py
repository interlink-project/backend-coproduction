import logging
import requests
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from app.config import settings
from app.general.db.session import SessionLocal

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
def wait_for_database() -> None:
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
def wait_for_ACL() -> None:
    try:
        requests.get(f"http://{settings.ACL_SERVICE_NAME}/healthcheck").json()
    except Exception as e:
        logger.error(e)
        raise e

@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def wait_for_catalogue() -> None:
    try:
        requests.get(f"http://{settings.CATALOGUE_SERVICE_NAME}/healthcheck").json()
    except Exception as e:
        logger.error(e)
        raise e

def main() -> None:
    logger.info("Initializing service")
    wait_for_database()
    wait_for_ACL()
    wait_for_catalogue()
    logger.info("Services finished initializing")


if __name__ == "__main__":
    main()

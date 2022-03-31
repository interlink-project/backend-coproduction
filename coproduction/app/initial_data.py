import logging
import requests

from app import crud, schemas
from app.general.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_SCHEMA_NAME = "Default schema"


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def main() -> None:
    logger.info("Creating initial data")
    # db = SessionLocal()
    # db.close()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

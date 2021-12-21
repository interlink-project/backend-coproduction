import logging
from app.general.prestart_functions import waitForDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    logger.info("Initializing service")
    waitForDatabase()
    logger.info("Services finished initializing")


if __name__ == "__main__":
    main()

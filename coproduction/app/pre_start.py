import asyncio
import logging
from app.waits import wait_for_catalogue, wait_for_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main() -> None:
    logger.info("Initializing service")
    wait_for_database()
    wait_for_catalogue()
    logger.info("Services finished initializing")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

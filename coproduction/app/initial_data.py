import asyncio
import logging
from app.general.db.session import SessionLocal
from app.messages import set_logging_disabled

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


async def init():
    db = SessionLocal()
    set_logging_disabled(True)
    db.close()

if __name__ == "__main__":
    logger.info("Creating initial data")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    logger.info("Initial data created")
    

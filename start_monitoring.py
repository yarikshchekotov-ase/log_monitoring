from monitoring_service.monitoring import AsyncDemon
from monitoring_service.loader import ConfigLoad
from service_log_manager.log_manager import LogManager
import validators
import logging
from service_log_manager.archiver import Archiver
import asyncio

logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] | [%(asctime)s] | %(name)s | %(message)s")

logger = logging.getLogger(__name__)

async def main():
    con = ConfigLoad("config.json")
    config = con.conf_load()
    log_path = config["log_path"]
    max_size = config["max_size_bytes"]
    urls = config["urls"]
    valid_urls = []
    for url in urls:
        if validators.url(url):
            valid_urls.append(url)
        else:
            logger.info("URL адрес не верный")
    archiver = Archiver("service_log_manager/logs")
    log_manager = LogManager(log_path, max_size, archiver)
    checker = AsyncDemon(valid_urls, log_path, log_manager)
    await checker.checker()
try:
    if __name__ == "__main__":
        asyncio.run(main())
except KeyboardInterrupt:
    logger.exception("Завершение программы")
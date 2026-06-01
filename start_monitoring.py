from monitoring_service.monitoring import AsyncDaemon
from monitoring_service.loader import ConfigLoad
import validators
import logging
from monitoring_service.archiver import Archiver
import asyncio


logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] | [%(asctime)s] | %(name)s | %(message)s")

logger = logging.getLogger(__name__)

async def main():
    try:
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
        dir = "service_log_manager\\logs"
        archiver = Archiver(log_path, max_size, dir)
        checker = AsyncDaemon(valid_urls, log_path, archiver)
        await checker.checker()
    except Exception as e:
        logger.exception(f"Error {e}")
try:
    if __name__ == "__main__":
        asyncio.run(main())
except KeyboardInterrupt:
    logger.exception("Завершение программы")
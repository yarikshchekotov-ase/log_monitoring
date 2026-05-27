from monitoring import Demon
from loader import ConfigLoad
from log_manager import LogManager
import validators
import logging
from archiver import Archiver


logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] | [%(asctime)s] | %(name)s | %(message)s")

logger = logging.getLogger(__name__)

def main():
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
    archiver = Archiver("logs")
    logmanager = LogManager(log_path, max_size, archiver)
    checker = Demon(valid_urls, log_path, logmanager)
    checker.checker()
try:
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    logger.exception("Завершение программы")
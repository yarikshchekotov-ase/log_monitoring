from faststream import FastStream
from faststream.rabbit import RabbitBroker
from log_manager import LogManager
import logging
import asyncio

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = FastStream(broker)

async def start_log_manager():
    logs_on_pus_in_loki = []
    service = "start"
    env = "dev"
    log_manager = LogManager(logs_on_pus_in_loki, service, env)
    await app.run()

try:
    if __name__ == "__main__":
        asyncio.run(start_log_manager())
except KeyboardInterrupt:
    logging.info("Останавливаяем сервис логирования")
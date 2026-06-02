from faststream import FastStream
from faststream.rabbit import RabbitBroker
from log_manager import LogManager
import logging
import asyncio
import time 
from monitoring_service.loader import ConfigLoad
from faststream.rabbit import RabbitBroker, RabbitQueue


con = ConfigLoad("config.json")
config = con.conf_load()
env = config["env"]
service = config["service_log_manager"]
log_manager = LogManager(service, env)
rabbitmq_config_url = config["rabbitmq_config_url"]
broker = RabbitBroker(rabbitmq_config_url)
app = FastStream(broker)

@broker.subscriber(RabbitQueue("logging_analysis", durable=True))
async def take_json_from_monitoring(service: str, env: str, logs: list[list[str]]):
    all_logs_push_loki = []
    try:
        for log in logs:
            level = log[0]
            message = log[1]
            status = log[2]
            url = log[3]
            timestamp = time.time_ns()
            new_log = "|".join([level, message, status, url])
            all_logs_push_loki.append([str(timestamp), new_log])
            await log_manager.push_logs_in_loki(all_logs_push_loki)
    except ConnectionError:
        logging.exception("Очищааем список логов на пуш, возращаем логи в очередь")
        raise ConnectionError

async def start_log_manager():
    await app.run()



try:
    if __name__ == "__main__":
        asyncio.run(start_log_manager())
except KeyboardInterrupt:
    logging.info("Останавливаяем сервис логирования")
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from log_manager import LogManager
import logging
import asyncio
import time 
from monitoring_service.loader import ConfigLoad
from faststream.rabbit import RabbitBroker, RabbitQueue

all_logs_push_loki = []
'''TODO: 
убрать переменые окружения либо в конфиг либо в .env'''
service = "start"
env = "dev"
log_manager = LogManager(all_logs_push_loki, service, env)
con = ConfigLoad("config.json")
config = con.conf_load()
rabbitmq_config_url = config["rabbitmq_config_url"]
broker = RabbitBroker(rabbitmq_config_url)
app = FastStream(broker)

@broker.subscriber(RabbitQueue("logging_analysis", durable=True))
async def take_json_from_monitoring(service: str, env: str, logs: list[list[str]]):
    for log in logs:
        level = log[0]
        message = log[1]
        status = log[2]
        url = log[3]
        timestamp = time.time_ns()
        new_log = "|".join([level, message, status, url])
        all_logs_push_loki.append([str(timestamp), new_log])
        '''TODO: серьезный баг
        Если база данных Loki ляжет то данные которые будут приходить из RabbitMQ будут пропадать из за обнуления списка в методе push_logs_in_loki первой задачей
        добавить в push_logs_in_loki: try except и вручную настроить выброс ошибок что бы внутри exept выполнять действия которые сохранят данные о логах'''
        await log_manager.push_logs_in_loki()

async def start_log_manager():
    await app.run()



try:
    if __name__ == "__main__":
        asyncio.run(start_log_manager())
except KeyboardInterrupt:
    logging.info("Останавливаяем сервис логирования")
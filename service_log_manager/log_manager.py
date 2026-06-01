from httpx import AsyncClient
from faststream.rabbit import RabbitBroker
from faststream import FastStream
from monitoring_service.loader import ConfigLoad
import logging

client = AsyncClient(timeout=10.0)

con = ConfigLoad("config.json")
config = con.conf_load()
rabbitmq_config_url = config["rabbitmq_config_url"]
broker = RabbitBroker(rabbitmq_config_url)
app = FastStream(broker)


class LogManager():
    def __init__(self, service, env):
        self.service = service
        self.env = env

    async def push_logs_in_loki(self,all_logs_push_loki):
        try:
            logs = {
                "streams": [
                    {
                        "stream": {
                            "service": self.service,
                            "env": self.env,
                        },
                        "values": all_logs_push_loki
                    }
                ]
            }
            '''TODO: в окончательной версии проекта нужно будет заменить localhost на loki т.к внутри сети докер будет ссылать именно на него'''
            await client.post("http://localhost:3100/loki/api/v1/push", json=logs)
        except Exception as e:
            logging.exception("База данных локи не отвечает")
            raise ConnectionError
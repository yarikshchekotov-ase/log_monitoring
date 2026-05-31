from httpx import AsyncClient
from faststream.rabbit import RabbitBroker
from faststream import FastStream
from datetime import datetime

client = AsyncClient(timeout=10.0)


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = FastStream(broker)


class LogManager():
    def __init__(self, all_logs_push_loki, service, env):
        self.all_logs_push_loki = all_logs_push_loki
        self.service = service
        self.env = env

    async def push_logs_in_loki(self):
        logs = {
            "streams": [
                {
                    "stream": {
                        "service": self.service,
                        "env": self.env,
                    },
                    "values": self.all_logs_push_loki
                }
            ]
        }
        await client.post("http://localhost:3100/loki/api/v1/push", json=logs)
        self.all_logs_push_loki = []
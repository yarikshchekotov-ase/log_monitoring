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

    @broker.subscriber("logging_analysis")
    async def take_json_from_monitoring(self, service: str, env: str, logs: list[list[str]]):
        self.env = env
        self.service = service
        for log in logs:
            level = log[0]
            message = log[1]
            status = log[2]
            url = log[3]
            timestamp = log[4]
            new_log = "|".join([level, message, status, url])
            self.all_logs_push_loki.append([timestamp, new_log])
        await self.push_logs_in_loki()
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
        await client.post("http://loki:3100/loki/api/v1/push", json=logs)
        self.all_logs_push_loki = []
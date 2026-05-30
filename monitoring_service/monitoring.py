import requests
import httpx
import asyncio
import logging
import time
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge

site_check_error = Counter("site_error_count", "need_for_test_my_app", labelnames=["url"])
site_check_succes = Counter("site_succes_conut", "need_for_test_my_app", labelnames=["url"])
site_speed = Gauge("site_speed_app", "need_for_test_my_app", labelnames=["url"])

async def check_url_async(client, url):
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        try:
            start_time = time.perf_counter()

            req = await client.get(url, timeout=5.0) # отправляем запрос на сайт
            end_time = time.perf_counter()

            site_speed.labels(url=url).set(end_time-start_time)

            logging.info(req.status_code)
            if req.status_code == 200: # смотрим статус кода
                site_check_succes.labels(url=url).inc()
                return f"[INFO] Website is up and running: {url}, {timestamp}\n"
            elif req.status_code == 500:
                site_check_error.labels(url=url).inc()
                return f"[CRITICAL] Website is DOWN! Status code: {req.status_code}, {timestamp}\n"
        except httpx.RequestError as e:
            site_check_error.labels(url=url).inc()
            return f"[CRITICAL] Connection error for {url}, {timestamp}\n"



class AsyncDemon():
    def __init__(self, urls, logs_path, log_manager):
        self.urls = urls
        self.logs_path = logs_path
        self.logmanager = log_manager
        self.is_runnig = True
    async def checker(self):
        start_http_server(8001)
        async with httpx.AsyncClient(timeout=5.0) as client:
            while self.is_runnig:
                try:
                    self.logmanager.logs()
                    tasks = [check_url_async(client, url) for url in self.urls]
                    logs = await asyncio.gather(*tasks)
                    with open(self.logs_path, 'a') as file:
                        file.writelines(logs)
                except KeyboardInterrupt:
                    logging.exception("Завершение программы")
                    self.is_runnig = False
                except Exception:
                    logging.exception("ERROR")
                    break
                await asyncio.sleep(60)
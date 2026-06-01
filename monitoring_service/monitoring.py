import httpx
import asyncio
import logging
import time
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge
import aiofiles
import os

site_check_error = Counter("site_error_count", "need_for_test_my_app", labelnames=["url"])
site_check_succes = Counter("site_succes_conut", "need_for_test_my_app", labelnames=["url"])
site_speed = Gauge("site_speed_app", "need_for_test_my_app", labelnames=["url"])


async def check_url_async(client, url):
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        try:
            start_time = time.perf_counter()
            '''TODO: Риск SSRF-атак 
            1) добавить в конфиг список урл куда не слать запрос
            2) Добавить проверку урл на уровне DNS -> socket.gethostbyname'''
            req = await client.get(url, timeout=5.0) # отправляем запрос на сайт
            end_time = time.perf_counter()
            site_speed.labels(url=url).set(end_time-start_time)
            logging.info(req.status_code)
            if req.status_code == 200: # смотрим статус кода
                site_check_succes.labels(url=url).inc()
                return f"[INFO] | Website is up and running | Status code: {req.status_code} | {url} | {timestamp}\n"
            elif req.status_code == 500:
                site_check_error.labels(url=url).inc()
                return f"[CRITICAL] | Website is DOWN! | Status code: {req.status_code} | {url} | {timestamp}\n"
            elif req.status_code == 503:
                site_check_error.labels(url=url).inc()
                return f"[CRITICAL] | Website isn`t available! | Status code: {req.status_code} | {url}| {timestamp}\n"
            else:
                return f"[WARNING] | Client Error | Status code: {req.status_code} | {url} | {timestamp}\n"
        except httpx.RequestError as e:
            site_check_error.labels(url=url).inc()
            return f"[CRITICAL] | Connection error for | 404 | {url} | {timestamp}\n"



class AsyncDaemon():
    def __init__(self, urls, log_path, archiver, max_size):
        self.urls = urls
        self.log_path = log_path
        self.archiver = archiver
        self.is_runnig = True
        self.max_size = max_size
    async def checker(self):
        start_http_server(8001)
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client: 
            while self.is_runnig:
                try:
                    # здесь отправка архивного файла в папку logs?
                    await asyncio.to_thread(self.archiver.logs)
                    
                    tasks = [check_url_async(client, url) for url in self.urls]
                    logs = await asyncio.gather(*tasks)
                    async with aiofiles.open(self.logs_path, 'a') as file:
                        await file.writelines(logs)
                        
                    await self.archiver.send_to_rabbit()
                except KeyboardInterrupt:
                    logging.exception("Завершение программы")
                    self.is_runnig = False
                except Exception:
                    logging.exception("ERROR")
                    break
                await asyncio.sleep(60)
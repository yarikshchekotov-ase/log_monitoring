from concurrent.futures import ThreadPoolExecutor
import requests
import time
import logging
from datetime import datetime

def check_url(url):
        try:
            req = requests.get(url, timeout=5) # отправляем запрос на сайт
            logging.info(req.status_code)
            time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            if req.status_code == 200: # смотрим статус кода
                
                return f"[INFO] Website is up and running: {url}, {time}\n"
            else:
                return f"[CRITICAL] Website is DOWN! Status code: {req.status_code}, {time}\n"
        except requests.exceptions.RequestException:
            return f"[CRITICAL] Connection error for {url}, {time}:\n"



class Demon():
    def __init__(self, urls, logs_path, logmanager):
        self.urls = urls
        self.logs_path = logs_path
        self.logmanager = logmanager 
    def checker(self):
        with ThreadPoolExecutor(max_workers=3) as executor:
            while True:
                try:
                    self.logmanager.logs()
                    res = executor.map(check_url, self.urls)
                    logs = list(res)
                    with open(self.logs_path, 'a') as file:
                        file.writelines(logs)
                    time.sleep(60)
                except Exception:
                    logging.exception("ERROR")
                    break
                except KeyboardInterrupt:
                    logging.exception("Завершение программы")
                    break
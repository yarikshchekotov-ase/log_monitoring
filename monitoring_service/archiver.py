import os
import logging
from datetime import datetime
import shutil
from faststream.rabbit import RabbitBroker
import glob
import logging
import aiofiles
import asyncio
from loader import ConfigLoad

con = ConfigLoad("config.json")
config = con.conf_load()
rabbitmq_config_url = config["rabbitmq_config_url"]
env = config["env"]
service = config["service_monitoring"]

broker = RabbitBroker(rabbitmq_config_url)


class Archiver():
    def __init__(self,log_path=None, max_size=None, dir=None):
        self.log_path = log_path
        self.max_size = max_size
        self.dir = dir
    def logs(self):
        '''привызове в демоне этот метод оборачивается в asyncio.to_thread() поэтому не смотря на синхроность данный метод уходит в отдельный поток и не мешает основному'''
        try:
            if os.path.exists(self.log_path):
                path_size = os.path.getsize(self.log_path) # возвращает размер файла в байтах
                if path_size > int(self.max_size): # проверка условия
                    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
                    new_filename = f"log_{timestamp}_{os.path.basename(self.log_path)}" # файл app_log.txt -> превращается файл log_время сейчас_app_log.txt
                    os.rename(self.log_path, f"{new_filename}")
                    with open(self.log_path, "a") as file:
                        file.write(f"[INFO] | Log rotated successfully | 200 | http://localhost:8000 |{timestamp}\n")
                        logging.info("Выполнено успешно")
            else:
                logging.info("Файл не найден или размер меньше")
        except Exception as e:
            logging.exception(f"Error: {e}")


    def logs_in_dir(self, file_log):
        if not os.path.exists(file_log):
            return
        
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)
        
        destination = os.path.join(self.dir, file_log)
        shutil.move(file_log, destination)


    async def file_logs_to_rabbitmq(self, log_file):
        async with aiofiles.open(log_file, 'r') as f:
            is_read = True
            all_logs = []
            while is_read:
                log = await f.readline()
                if log == "\n":
                    continue
                if not log:
                    is_read = False
                else:
                    log = log.strip()
                    part_log = log.split('|')
                    level = part_log[0]
                    message = part_log[1]
                    status_code = part_log[2]
                    url = part_log[3]
                    timestamp = part_log[4]
                    logg = [level,
                            message,
                            status_code,
                            url,
                            timestamp]
                    all_logs.append(logg)
        os.remove(log_file)
        async with broker:
            await broker.publish(
                        message={
                                "service": service,
                                "env": env,
                                "logs": all_logs
                    } , queue="logging_analysis",routing_key=''
            )

    async def send_to_rabbit(self):
            found_logs_file = glob.glob("service_log_manager\\log_*.txt")
            for log_file in found_logs_file:
                await asyncio.to_thread(self.logs_in_dir, log_file)
            logs_file = glob.glob("service_log_manager\\logs\\log_*.txt")
            if logs_file:
                for log in logs_file:
                    await self.file_logs_to_rabbitmq(log)
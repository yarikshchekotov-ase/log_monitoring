import os
import logging
from datetime import datetime
import shutil
from faststream.rabbit import RabbitBroker
import glob
import logging
import aiofiles

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")


class Archiver():
    def __init__(self,log_path=None, max_size=None, dir=None):
        self.log_path = log_path
        self.max_size = max_size
        self.dir = dir
    def logs(self):
        try:
            if os.path.exists(self.log_path):
                path_size = os.path.getsize(self.log_path) # возвращает размер файла в байтах
                if path_size > int(self.max_size): # проверка условия
                    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
                    new_filename = f"log_{timestamp}_{os.path.basename(self.log_path)}"
                    os.rename(self.log_path, f"{new_filename}")
                    self.logs_in_dir(f"{new_filename}")
                    with open(self.log_path, "a") as file:
                        file.write(f"[INFO] | Log rotated successfully | 200 | None |{timestamp}\n")
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
                if not log:
                    is_read = False
                else:
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
        await broker.publish(
                "Hi!",
                queue="test",
                exchange=""
                #     message={
                #             "service": "monitoring",
                #             "env": "dev",
                #             "logs": all_logs
                # } , queue="logging_analysis",routing_key=''
        )
    
    async def send_to_rabbit(self):
            logs_file = glob.glob("service_log_manager\\logs\\*.txt")
            await broker.connect()
            if logs_file:
                for log in logs_file:
                    await self.file_logs_to_rabbitmq(log)

            await broker.close()
        
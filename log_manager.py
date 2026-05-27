import os
import logging
from datetime import datetime
class LogManager():
    def __init__(self,log_path, max_size, archiver):
        self.log_path = log_path
        self.max_size = max_size
        self.archiver = archiver
    def logs(self):
        try:
            if os.path.exists(self.log_path):
                path_size = os.path.getsize(self.log_path) # возвращает размер файла в байтах
                if path_size > int(self.max_size): # проверка условия
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    new_filename = f"log_{timestamp}_{os.path.basename(self.log_path)}"
                    os.rename(self.log_path, f"{new_filename}")
                    self.archiver.logs_in_dir(f"{new_filename}")
                    with open(self.log_path, "a") as file:
                        file.write("[INFO] Log rotated successfully\n")
                        logging.info("Выполнено успешно")
            else:
                logging.info("Файл не найден или размер меньше")
        except Exception as e:
            logging.exception(f"Error: {e}")
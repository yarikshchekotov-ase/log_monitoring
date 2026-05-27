import os
import logging

class LogManager():
    def __init__(self,log_path, max_size):
        self.log_path = log_path
        self.max_size = max_size
    def logs(self):
        try:
            if os.path.exists(self.log_path):
                path_size = os.path.getsize(self.log_path) # возвращает размер файла в байтах
                if path_size > int(self.max_size): # проверка условия
                    os.rename(self.log_path, "app.log.old")
                    
                    if os.path.exists("app.log.old"):
                        os.remove("app.log.old")
                    with open(self.log_path, "a") as file:
                        file.write("[INFO] Log rotated successfully\n")
                        logging.info("Выполнено успешно")
            else:
                logging.info("Файл не найден или размер меньше")
        except Exception as e:
            logging.exception(f"Error: {e}")
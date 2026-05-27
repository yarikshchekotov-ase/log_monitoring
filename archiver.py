import os
import shutil

class Archiver():
    def __init__(self, dir):
        self.dir = dir
    def logs_in_dir(self, file_log):
        if not os.path.exists(file_log):
            return
        
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)
        
        destination = os.path.join(self.dir, file_log)
        shutil.move(file_log, destination)

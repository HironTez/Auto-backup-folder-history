import time
import sys
import os
import shutil
import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class OnMyWatch:
    # Set the directory on watch
    watchDirectory = json.loads(open("options.txt", "r").read().replace("\\", "\\\\"))["backup_source_path"]
  
    def __init__(self):
        self.observer = Observer()
  
    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
  
        self.observer.join()
  
  
class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        backup = Backup()
        if backup.check_time_last_backup():
            backup.create_new()
            backup.delete_old()

class Backup:
    def __init__(self):
        self.options = json.loads(open("options.txt", "r").read().replace("\\", "\\\\"))

    def create_new(self):
        shutil.copytree(self.options["backup_source_path"], self.options["backup_path"] + "\\" + str(time.time()))

    def delete_old(self):
        _, folders, _ = next(os.walk(self.options["backup_path"]))
        if len(folders) > self.options["number_of_old_copies_kept"]:
            the_oldest_folder = sorted(folders)[0]
            shutil.rmtree(self.options["backup_path"] + the_oldest_folder)

    def check_time_last_backup(self):
        _, folders, _ = next(os.walk(self.options["backup_path"]))
        if len(folders) != 0:
            time_last_backup = float(sorted(folders)[-1])
            if time_last_backup + self.options["minimum_time_between_backups"] <= time.time():
                return True
            else:
                return False
        else:
            return True
  
if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()
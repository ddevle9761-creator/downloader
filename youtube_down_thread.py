import os
from  pathlib import Path
import subprocess

from yt_dlp import YoutubeDL
from PySide6.QtCore import QObject, Signal, Slot, QCoreApplication

CUR_DIR = Path(__file__).resolve().parent.absolute()
VIDEOS_DIR = Path.joinpath(CUR_DIR, 'Videos')


class TelechargementWorker(QObject):
    stop = Signal(object)
    finished = Signal()
    error = Signal(str)

    def __init__(self, /,url, path=None):
        super().__init__()
        if path is None:
            path = VIDEOS_DIR
        self.path = path
        self.url = url
        self.youtube = YoutubeDL()

    @Slot()
    def run(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        try:
            os.chdir(self.path)

            url_list = [self.url]
            self.youtube.download(url_list)
            prefixe = (".avi", ".mp3", ".webm", ".mkv", ".flv")
            for i in self.path.iterdir():
                if i in prefixe:
                    print(i)


        except Exception as exc:
            self.error.emit(str(exc))

        finally:
            self.finished.emit()


    @Slot()
    def stop(self):
        if self.youtube:
            self.youtube.close()



if __name__ == '__main__':
    path = os.getcwd()
    path = os.path.abspath(f"{path}/Videos")
    path = os.path.abspath(path)
    prefi = (".avi", ".mp3", ".webm", ".mkv", ".flv")
    formate = ".mp4"
    for url in os.listdir(path):
        if os.path.splitext(url)[1] != formate:
            try:
                subprocess.run(["ffmpeg", "-i", f"{url}", "-c:v", "libx264", "-c:a", f"{os.path.splitext(url)[1]}.{formate}"], shell=True, check=True, universal_newlines=True, stdout=subprocess.DEVNULL)
            except Exception as exc:
                pass

            print(url)
            print(os.path.splitext(url)[1])












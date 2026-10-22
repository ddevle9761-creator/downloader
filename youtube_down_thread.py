import os
from pathlib import Path
import subprocess
from threading import Event

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from PySide6.QtCore import QObject, Signal, Slot

CUR_DIR = Path(__file__).resolve().parent.absolute()
VIDEOS_DIR = Path.joinpath(CUR_DIR, 'Videos')


class TelechargementWorker(QObject):
    finished = Signal(bool, bool, str)
    progress = Signal(int)

    def __init__(self, /, url, path=None):
        super().__init__()
        if path is None:
            path = VIDEOS_DIR
        self.path = Path(path)
        self.url = url
        self.youtube = None
        self._stop_requested = Event()
        self._cancelled = False
        self._error_message = ""

    @Slot()
    def run(self):
        try:
            self.path.mkdir(parents=True, exist_ok=True)
            self.youtube = YoutubeDL({
                "outtmpl": str(self.path / "%(title)s.%(ext)s"),
                "progress_hooks": [self._update_progress],
            })
            self.youtube.download([self.url])
            if self._stop_requested.is_set():
                self._cancelled = True
                return

            for source in self.path.iterdir():
                if self._stop_requested.is_set():
                    self._cancelled = True
                    break
                if source.is_file() and source.suffix.lower() in {".avi", ".mkv", ".flv", ".webm"}:
                    destination = source.with_suffix(".mp4")
                    subprocess.run(
                        [
                            "ffmpeg",
                            "-y",
                            "-i",
                            str(source),
                            "-c:v",
                            "libx264",
                            "-c:a",
                            "aac",
                            str(destination),
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    if self._stop_requested.is_set():
                        self._cancelled = True
                        break

        except Exception as exc:
            if self._stop_requested.is_set():
                self._cancelled = True
            else:
                self._error_message = str(exc)

        finally:
            if self.youtube is not None:
                try:
                    self.youtube.close()
                except Exception as exc:
                    if not self._error_message and not self._cancelled:
                        self._error_message = str(exc)
            success = not self._error_message and not self._cancelled
            self.finished.emit(success, self._cancelled, self._error_message)

    def _update_progress(self, details):
        if self._stop_requested.is_set():
            raise DownloadError("Téléchargement annulé")

        if details.get("status") == "finished":
            self.progress.emit(99)
            return

        downloaded = details.get("downloaded_bytes")
        total = details.get("total_bytes") or details.get("total_bytes_estimate")
        if downloaded is not None and total:
            self.progress.emit(min(100, int(downloaded * 100 / total)))

    @Slot()
    def request_stop(self):
        self._stop_requested.set()



if __name__ == '__main__':
    pass
    # path = os.getcwd()
    # path = os.path.abspath(f"{path}/Videos")
    # path = os.path.abspath(path)
    # YouTube = YoutubeDL()
    # info = youtube.extract_info(url="https://www.youtube.com/shorts/6EtsaDJgYc8", download=False, force_generic_extractor= True, process=True)
    # for i in info.items():
    #     print(i)

    # prefi = (".avi", ".mp3", ".webm", ".mkv", ".flv")
    # formate = ".mp4"
    # for url in os.listdir(path):
    #     if os.path.splitext(url)[1] != formate:
    #         try:
    #             subprocess.run(["ffmpeg", "-i", f"{url}", "-c:v", "libx264", "-c:a", f"{os.path.splitext(url)[1]}.{formate}"], shell=True, check=True, universal_newlines=True, stdout=subprocess.DEVNULL)
    #         except Exception as exc:
    #             pass
    #
    #         print(url)
    #         print(os.path.splitext(url)[1])



# def afficher_message(message):
#     print(f"Message depuis le thread : {message}")
#
# # Liste de messages à afficher
# messages = ["Bonjour", "Salut", "Hello", "Hola"]
#
# # Création de plusieurs threads
# threads = []
# for message in messages:
#     thread = threading.Thread(target=afficher_message, args=(message,))
#     threads.append(thread)
#     thread.start()
#
# # Attente de la fin de tous les threads
# for thread in threads:
#     thread.join()
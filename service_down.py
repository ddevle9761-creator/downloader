import os
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Signal, Qt

from youtube_down_thread import TelechargementWorker


class ServiceDown(QObject):
    progress = Signal(int)
    finished = Signal(bool, bool, str)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url
        self.thread = None
        self.worker = None
        self._result = (False, False, "")

    def start(self):
        if self.is_running():
            raise RuntimeError("Un téléchargement est déjà en cours")

        self.__check_text__()
        self._result = (False, False, "")
        self.thread = QThread(self)
        self.worker = TelechargementWorker(self.url)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress)
        self.worker.finished.connect(self._capture_result, Qt.ConnectionType.DirectConnection)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self._on_thread_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def is_running(self):
        return self.thread is not None and self.thread.isRunning()

    def __check_text__(self):
        if self.url and self.url.startswith("https://"):
            return True
        raise ValueError("Veuillez entrer une URL valide")

    def stop(self):
        if self.worker is not None and self.is_running():
            self.worker.request_stop()

    def _capture_result(self, success, cancelled, error_message):
        self._result = (success, cancelled, error_message)

    def _on_thread_finished(self):
        self.thread = None
        self.worker = None
        self.finished.emit(*self._result)


if __name__ == "__main__":
    path = os.path.join(os.getcwd(), "Videos")
    path = Path(path)
    for file in os.listdir(path):
        if file.endswith(".webm"):
            print(file)


    # service = ServiceDown("https://www.youtube.com/shorts/bR1eESW6Z2I?t=3&feature=share")
    #
    # service.start()

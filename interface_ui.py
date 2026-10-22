from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QHBoxLayout
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6 import QtWidgets, QtCore
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QMessageBox, QProgressBar
import sys
from pathlib import Path
import time

from service_down import ServiceDown



class Dash(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("devle")

        self.setMaximumSize(1000, 600)
        self.setMinimumSize(1000, 600)
        self.text_edit = None
        self.btn = None
        self.download_service = None
        self._close_after_download = False
        self.setup_ui()
        self.connexion()
        self.charger_les_video()


    def setup_ui(self):
        vertical_layout = QtWidgets.QHBoxLayout(self)
        vertical_layout.setStretch(0, 4)
        vertical_layout.setStretch(1, 4)
        vertical_layout.setSpacing(10)
        layout_video = QtWidgets.QVBoxLayout()
        layout_widget = QtWidgets.QVBoxLayout()
        layout_widget.setSpacing(10)
        layout_video.setSpacing(10)
        layout_widget.setGeometry(QtCore.QRect(0, 0, 600, 500))
        layout_video.setGeometry(QtCore.QRect(0, 0, 700, 600))

        vertical_layout.addLayout(layout_widget)
        vertical_layout.addLayout(layout_video)



        self.vodeo_widget = QVideoWidget()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.vodeo_widget)



        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Entrer le url ici !")
        layout_widget.addWidget(self.text_edit)

        self.btn = QPushButton("Telecharger")
        self.btnAnuler = QPushButton("Anuler")

        self.btn.setMaximumSize(QtCore.QSize(300, 50))
        self.btnAnuler.setMaximumSize(QtCore.QSize(300, 50))

        layout_top_btn = QHBoxLayout()
        layout_top_btn.minimumHeightForWidth(100)
        layout_top_btn.addWidget(self.btn)
        layout_top_btn.addWidget(self.btnAnuler)
        layout_widget.addLayout(layout_top_btn, QtCore.Qt.AlignmentFlag.AlignTop)

        self.listes = QListWidget()
        self.listes.setMaximumSize(QtCore.QSize(700, 600))
        self.listes.setMinimumSize(QtCore.QSize(700, 600))
        title = QtWidgets.QLabel("<h1 style='color:cyan; text-align:center'> La liste des videos </h1>".title())
        layout_widget.addWidget(title)
        layout_widget.addWidget(self.listes, 1)

        self.progress = QProgressBar()

        self.progress.setMaximum(100)
        self.progress.setValue(0)
        layout_nav = QtWidgets.QHBoxLayout()
        self.BtnStop = QPushButton("Stop")
        self.BtnStart = QPushButton("Start")
        self.BtnRestart = QPushButton("Restart")
        layout_nav.addWidget(self.BtnRestart)
        layout_nav.addWidget(self.BtnStart)
        layout_nav.addWidget(self.BtnStop)




        layout_video.addWidget(self.vodeo_widget)
        layout_video.addLayout(layout_nav)
        layout_video.addWidget(self.progress)



    def connexion(self):
        self.btn.clicked.connect(self.set_text)
        self.btnAnuler.clicked.connect(self.annuler_telechargement)
        self.listes.itemClicked.connect(self.recuperer_video)
        self.btnAnuler.setEnabled(False)
        self.BtnStop.clicked.connect(self.stop_video)
        self.BtnStart.clicked.connect(self.start_video)
        self.BtnRestart.clicked.connect(self.restart_video)

        #self.la_duration()



    def get_text(self):
        if not self.text_edit:
            return False
        text = self.text_edit.text()
        return text


    def set_text(self):
        text = self.get_text()
        if not text or (self.download_service and self.download_service.is_running()):
            return

        tele = ServiceDown(str(text), self)
        tele.progress.connect(self.progress.setValue)
        tele.finished.connect(self._telechargement_termine)
        try:
            tele.start()
        except (ValueError, RuntimeError) as exc:
            QMessageBox.warning(self, "Erreur", str(exc))
            return

        self.download_service = tele
        self.progress.setValue(0)
        self.btn.setEnabled(False)
        self.btnAnuler.setEnabled(True)
        self.text_edit.clear()

    def annuler_telechargement(self):
        if self.download_service and self.download_service.is_running():
            self.download_service.stop()
            self.btnAnuler.setEnabled(False)

    def _telechargement_termine(self, success, cancelled, error_message):
        self.download_service = None
        self.btn.setEnabled(True)
        self.btnAnuler.setEnabled(False)

        if success:
            self.progress.setValue(100)
            QMessageBox.information(self, "Téléchargement", "Téléchargement terminé")
        elif cancelled:
            QMessageBox.information(self, "Téléchargement", "Téléchargement annulé")
        else:
            QMessageBox.warning(self, "Erreur", error_message or "Le téléchargement a échoué")

        if self._close_after_download:
            self._close_after_download = False
            self.close()

    def closeEvent(self, event):
        if self.download_service and self.download_service.is_running():
            self._close_after_download = True
            self.download_service.stop()
            event.ignore()
            return
        super().closeEvent(event)

    def charger_les_video(self):
        extention = (".mp4", ".avi", ".mkv", ".flv", ".webm")
        path = Path(__file__).resolve().parent / "Videos"
        if path.is_dir():

            for file in path.iterdir():
                if file.suffix in extention:
                    item = QListWidgetItem(file.name)
                    item.setData(Qt.ItemDataRole.UserRole, file)
                    self.listes.addItem(item)


    def recuperer_video(self, item):
        fill_path = item.data(Qt.ItemDataRole.UserRole)
        video_url = QUrl.fromLocalFile(fill_path)
        self.player.setSource(video_url)
        self.player.play()


    def start_video(self):
        if self.player.isPlaying():
            return
        self.player.play()


    def stop_video(self):
        if self.player.isPlaying():
            self.player.pause()

    def la_duration(self):
        if self.player.isPlaying(): pass
        duration = self.player.duration()
        print(duration)

    def restart_video(self):
        if self.player.isPlaying():
            self.player.stop()
            self.player.play()











if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Dash()
    try:
        with open("../../assets/styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass
    window.show()
    sys.exit(app.exec())

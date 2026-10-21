from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6 import QtWidgets, QtCore
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QMessageBox, QProgressBar
import sys
from pathlib import Path

from service_down import ServiceDown



class Dash(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dash")
        self.resize(1000, 600)
        self.text_edit = None
        self.btn = None
        self.setup_ui()
        self.connexion()
        self.charger_les_video()


    def setup_ui(self):
        vertical_layout = QtWidgets.QHBoxLayout(self)
        layout_video = QtWidgets.QVBoxLayout()
        layout_widget = QtWidgets.QVBoxLayout()

        vertical_layout.addLayout(layout_widget)
        vertical_layout.addLayout(layout_video)



        self.vodeo_widget = QVideoWidget()

        self.vodeo_widget.setMinimumSize(QtCore.QSize(400, 300))
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.vodeo_widget)



        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Entrer le url ici !")
        layout_widget.addWidget(self.text_edit)

        self.btn = QPushButton("Telecharger")
        self.btn.setMaximumSize(QtCore.QSize(110, 50))
        layout_widget.addWidget(self.btn)

        self.listes = QListWidget()
        self.listes.setMaximumSize(QtCore.QSize(700, 600))
        layout_widget.addWidget(self.listes, 1)

        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        layout_widget.addWidget(self.progress)



        layout_video.addWidget(self.vodeo_widget)
        layout_video.addWidget(self.progress)

    def connexion(self):
        self.btn.clicked.connect(self.set_text)
        self.listes.itemClicked.connect(self.recuperer_video)



    def get_text(self):
        if not self.text_edit:
            return False
        text = self.text_edit.text()
        return text


    def increment_progress(self):
        value = self.progress.value()
        if value < 100:
            self.progress.setValue(value + 100)




    def set_text(self):
        text = self.get_text()
        if text:
            try:
                tele = ServiceDown(str(text))
                if tele.__check_text__():
                    QMessageBox.information(self, "Télèchargement", "Télèchargement en cours")

                    self.increment_progress()
                    tele.start()


                    self.text_edit.clear()
                    QMessageBox.information(self, "Télèchargement", "Télèchargement terminée")

            except Exception as e:
                QMessageBox.warning(self, "error", f"{e}")
                self.text_edit.clear()

    def charger_les_video(self):
        extention = (".mp4", ".avi", ".mkv", ".flv", ".webm")
        path = Path("Videos")
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

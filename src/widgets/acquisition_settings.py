from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon


class AcquisitionControls(QWidget):

    start_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_start = QPushButton("Start")
        self.btn_pause = QPushButton("Pause")
        self.btn_stop = QPushButton("Stop")

        # Definindo ícones
        self.btn_start.setIcon(QIcon("icons/start.png"))
        self.btn_pause.setIcon(QIcon("icons/pause.png"))
        self.btn_stop.setIcon(QIcon("icons/stop.png"))

        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_pause)
        layout.addWidget(self.btn_stop)

        self.btn_start.clicked.connect(self.start_clicked.emit)
        self.btn_pause.clicked.connect(self.pause_clicked.emit)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)

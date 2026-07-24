from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon


class DarkControlsWidget(QWidget):

    dark_clicked = pyqtSignal()
    
    
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_dark = QPushButton("Dark")
        #self.btn_dark.setIcon(QIcon("icons/dark.png"))

        
        layout.addWidget(self.btn_dark)
        self.btn_dark.clicked.connect(self.dark_clicked.emit)


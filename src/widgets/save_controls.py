from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon


class SaveControlsWidget(QWidget):

    save_clicked = pyqtSignal()
    
    
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_save = QPushButton("Save")
        self.btn_save.setIcon(QIcon("icons/save.png"))

        
        layout.addWidget(self.btn_save)
        self.btn_save.clicked.connect(self.save_clicked.emit)


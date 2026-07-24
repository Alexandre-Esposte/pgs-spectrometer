from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon


class BaselineControlsWidget(QWidget):

    baseline_clicked = pyqtSignal()
    
    
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_baseline = QPushButton("Baseline")
        #self.btn_baseline.setIcon(QIcon("icons/baseline.png"))

        
        layout.addWidget(self.btn_baseline)
        self.btn_baseline.clicked.connect(self.baseline_clicked.emit)


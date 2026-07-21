from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton,QFrame
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon


class ScaleControlsWidget(QWidget):

    autoscale_clicked = pyqtSignal()
    scale_clicked = pyqtSignal()
    

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        #Auto Scale
        self.btn_autoscale = QPushButton("Auto Scale")
        self.btn_autoscale.setIcon(QIcon("icons/autoscale.png"))
        
        layout.addWidget(self.btn_autoscale)
        self.btn_autoscale.clicked.connect(self.autoscale_clicked.emit)

        #Scale
        self.btn_scale = QPushButton('Scale')
        self.btn_scale.setIcon(QIcon("icons/scale.png"))
        layout.addWidget(self.btn_scale)        
        self.btn_scale.clicked.connect(self.scale_clicked.emit)

import numpy as np
import pyqtgraph as pg

from pathlib import Path
from PyQt5.QtGui import QIcon
from configs.ccd_configs import ccdGraphStyles
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QThread, QRunnable, QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QToolBar, QAction, QLabel, QSpinBox, QComboBox



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PGS - Espectrometro CCD")
        self.resize(800, 400)


        # Cria o widget que conterá o gráfico dos dados do CCD
        self.ccd_graph = pg.PlotWidget()
        ccdGraphStyles(self.ccd_graph)


        # Disponibilizando widgets na janela principal
        self.setCentralWidget(self.ccd_graph)

        
        # Tool bars com funcionalidade de controle do CCD
        toolbar_ccd = QToolBar("CCD Controls")
        toolbar_ccd.setMovable(False)

        # Botoes de start, pause e stop
        self.action_start = QAction(QIcon("icons/start.png"),'Start CCD', self)
        self.action_stop = QAction(QIcon("icons/stop.png"), 'Stop CCD', self)
        self.action_pause = QAction(QIcon("icons/pause.png"), 'Pause CCD', self)

        toolbar_ccd.addAction(self.action_start)
        toolbar_ccd.addSeparator()
        toolbar_ccd.addAction(self.action_pause)
        toolbar_ccd.addSeparator()
        toolbar_ccd.addAction(self.action_stop)

        self.action_start.triggered.connect(self.start_ccd)
        self.action_stop.triggered.connect(self.stop_ccd)
        self.action_pause.triggered.connect(self.pause_ccd)
        
        
        # Integration Time Controls
        toolbar_ccd.addSeparator()
        toolbar_ccd.addWidget(QLabel("Integration time:"))

        self.integration_spin = QSpinBox()
        self.integration_spin.setRange(1, 10000)

        toolbar_ccd.addWidget(self.integration_spin)
        
        self.ordem_grandeza = QComboBox()
        self.ordem_grandeza.addItems(["s", "ms", "us"])
        toolbar_ccd.addWidget(self.ordem_grandeza)



        # Scans to average controls
        toolbar_ccd.addSeparator()
        toolbar_ccd.addWidget(QLabel("Scans to average:"))
        self.average_spin = QSpinBox()
        self.average_spin.setRange(1, 100)
        toolbar_ccd.addWidget(self.average_spin)


        # Apply
        self.action_apply = QAction("Aplicar Configurações", self)
        self.action_apply.triggered.connect(self.apply_settings)

        self.addToolBar(toolbar_ccd)
        toolbar_ccd.addAction(self.action_apply)


    def apply_settings(self):
        """
        Aplica configurações ajustadas pelo usuario no CCD
        """
        
        integration_time = self.integration_spin.value()
        ordem_grandeza = self.ordem_grandeza.currentText()

        if ordem_grandeza == "ms":
            integration_time *= 1e-3
        elif ordem_grandeza == "us":
            integration_time *= 1e-6

        scans_to_average = self.average_spin.value()

        print(f"Integration time: {integration_time} s")
        print(f"Scans to average: {scans_to_average}")

    def start_ccd(self):
        print("Iniciando aquisição do CCD...")
    def stop_ccd(self):
        print("Parando aquisição do CCD...")
    def pause_ccd(self):
        print("Pausando aquisição do CCD...")
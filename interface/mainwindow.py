import numpy as np
import pyqtgraph as pg

from pathlib import Path
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QThread, QRunnable, QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QToolBar, QAction, QLabel, QSpinBox, QComboBox, QCheckBox


# Configurações do grafico do pyqtraph
from layouts.ccd_graph import ccdGraphStyles

# Widgets personalizados
from widgets.acquisition_settings import AcquisitionControls
from widgets.ccd_settings import CCDSettingsWidget
from widgets.scale_controls import ScaleControlsWidget

# Workers
from workers.ccd_worker import CCDWorker


class MainWindow(QMainWindow):
    
    #-------------------------Criando sinais para botoes----------------    
    start_signal = pyqtSignal()
    stop_signal = pyqtSignal()
    pause_signal = pyqtSignal()
    update_settings_ccd_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()


        self.setWindowTitle("PGS - Espectrometro CCD")
        self.resize(900, 500)

   
        #---------------------------Configurando Threads  e Workers---------------------
        self._setup_worker()

        #---------------------------Cria o widget que conterá o gráfico dos dados do CCD----------------------------
        self.ccd_graph = pg.PlotWidget()
        ccdGraphStyles(self.ccd_graph)
        self.setCentralWidget(self.ccd_graph)
        self.curve = self.ccd_graph.plot()

        
       # =========================
        # Toolbar 1 - CCD Acquisition and Settings
        # =========================
        self.toolbar_acq = QToolBar("Acquisition")
        self.toolbar_acq.setMovable(False)

        self.acq_controls = AcquisitionControls()
        self.ccd_settings = CCDSettingsWidget()
            
        self.toolbar_acq.addWidget(self.acq_controls)
        self.toolbar_acq.addSeparator()  # Adiciona um separador visual entre os grupos de controles
        self.toolbar_acq.addWidget(self.ccd_settings)

        self.addToolBar(Qt.TopToolBarArea, self.toolbar_acq)

        # =========================
        # Break (nova linha)
        # =========================
        self.addToolBarBreak(Qt.TopToolBarArea)

        # # =========================
        # # Toolbar 2 - Settings
        # # =========================
        # self.toolbar_settings = QToolBar("Settings")
        # self.toolbar_settings.setMovable(False)
        self.toolbar_graph_settings = QToolBar("Graph Settings")
        self.toolbar_graph_settings.setMovable(False)

        self.scale_controls = ScaleControlsWidget()
        self.toolbar_graph_settings.addWidget(self.scale_controls)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar_graph_settings)

        # =========================
        # Connections
        # =========================
        self._connect_signals()

    def _connect_signals(self):

        # Acquisition
        self.acq_controls.start_clicked.connect(self.start_ccd)
        self.acq_controls.pause_clicked.connect(self.pause_ccd)
        self.acq_controls.stop_clicked.connect(self.stop_ccd)

        # Settings
        self.ccd_settings.settings_applied.connect(self.apply_settings)

        # Scale
        self.scale_controls.autoscale_clicked.connect(self.auto_scale_function)
    
    
    
    def start_ccd(self):
        print("Iniciando aquisição do CCD...")
        self.start_signal.emit()

    def stop_ccd(self):
        print("Parando aquisição do CCD...")
        self.stop_signal.emit()
        self.curve.setData(np.zeros(2048))

    def pause_ccd(self):
        print("Pausando aquisição do CCD...")
        self.pause_signal.emit()

    def auto_scale_function(self):
        print("Ajustando escala do gráfico...")

    def apply_settings(self, settings: dict):
        print("Aplicando configurações:")
        print(settings)
        self.worker.update_settings(settings)
        

    def auto_scale_function(self):
        print("Auto scale acionado.")
        self.ccd_graph.enableAutoRange()

    def update_graph(self, data: np.ndarray):
        self.curve.setData(data)


    def _setup_worker(self):

        self.thread = QThread()
        self.worker = CCDWorker()

        self.worker.moveToThread(self.thread)

        # Quando a thread iniciar → inicializa o worker (cria o timer na thread correta)
        self.thread.started.connect(self.worker.initialize)

        # Comunicação worker → GUI
        self.worker.data.connect(self.update_graph)

        self.start_signal.connect(self.worker.start)
        self.stop_signal.connect(self.worker.stop)
        self.pause_signal.connect(self.worker.pause)
        self.update_settings_ccd_signal.connect(self.worker.update_settings)

        self.thread.start()


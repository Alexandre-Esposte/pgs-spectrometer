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
from widgets.motor_controls import MotorControlsWidget

# Workers
from workers.ccd_worker import CCDWorker
from workers.motor_worker import MotorWorker


class MainWindow(QMainWindow):
    
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

        self.ccd_graph.enableAutoRange(x=True, y=False)

        self.curve = self.ccd_graph.plot(pen='r')

        
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
        # # Toolbar 2 - Scale
        # # =========================

        self.toolbar_graph_settings = QToolBar("Graph Settings")
        self.toolbar_graph_settings.setMovable(False)

        self.scale_controls = ScaleControlsWidget()
        self.toolbar_graph_settings.addWidget(self.scale_controls)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar_graph_settings)

        # # =========================
        # # Toolbar 2 - Motor
        # # =========================
        self.toolbar_graph_settings.addSeparator()
        self.motor_controls = MotorControlsWidget()
        self.toolbar_graph_settings.addWidget(self.motor_controls)


        # =========================
        # Connections
        # =========================
        self._connect_signals()

    def _connect_signals(self):

        # Acquisition
        self.acq_controls.start_clicked.connect(self.ccd_worker.start)
        self.acq_controls.pause_clicked.connect(self.ccd_worker.pause)
        self.acq_controls.stop_clicked.connect (self.ccd_worker.stop)

        # Settings
        self.ccd_settings.settings_applied.connect(self.ccd_worker.update_settings)

        # Scale
        self.scale_controls.autoscale_clicked.connect(self.auto_scale_function)

        # Motor buttons
        self.motor_controls.motor_command.connect(self.motor_worker.send_command)

    
    
    def auto_scale_function(self):
        print("Auto scale acionado.")
        self.ccd_graph.enableAutoRange()


    def update_graph(self, data: np.ndarray):
        self.curve.setData(data)

    def _setup_worker(self):

        # =========================
        # CCD Worker
        # =========================
        self.ccd_thread = QThread()
        self.ccd_worker = CCDWorker()

        self.ccd_worker.moveToThread(self.ccd_thread)
        self.ccd_thread.started.connect(self.ccd_worker.initialize)
        self.ccd_worker.data.connect(self.update_graph)
        self.ccd_thread.start()

        # =========================
        # Motor Worker
        # =========================
        self.motor_thread = QThread()
        self.motor_worker = MotorWorker()

        self.motor_worker.moveToThread(self.motor_thread)
        self.motor_thread.started.connect(self.motor_worker.initialize)

        self.motor_thread.start()

    def closeEvent(self, event):

        print("Encerrando threads...")

        # Finaliza thread do CCD
        if self.ccd_thread.isRunning():
            self.ccd_thread.quit()
            self.ccd_thread.wait()

        # Finaliza thread do Motor
        if self.motor_thread.isRunning():
            self.motor_thread.quit()
            self.motor_thread.wait()

        print("Threads finalizadas com sucesso.")

        event.accept()



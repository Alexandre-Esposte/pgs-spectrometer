import numpy as np
import pandas as pd
import pyqtgraph as pg

from pathlib import Path
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QThread, QRunnable, QTimer, QCoreApplication
from PyQt5.QtWidgets import (QApplication, 
                             QMainWindow,
                             QWidget, 
                             QVBoxLayout, 
                             QToolBar, 
                             QAction, 
                             QLabel, 
                             QSpinBox, 
                             QComboBox, 
                             QCheckBox,
                             QFileDialog,
                             QMessageBox)


# Configurações do grafico do pyqtraph
from layouts.ccd_graph import ccdGraphStyles

# Widgets personalizados
from widgets.acquisition_settings import AcquisitionControls
from widgets.ccd_settings import CCDSettingsWidget
from widgets.scale_controls import ScaleControlsWidget
from widgets.motor_controls import MotorControlsWidget
from widgets.encoder_view import EncoderViewerWidget
from widgets.save_controls import SaveControlsWidget
from widgets.baseline_controls import BaselineControlsWidget
from widgets.dark_controls import DarkControlsWidget

# Workers
from workers.ccd_worker import CCDWorker
from workers.motor_worker import MotorWorker
from workers.encoder_worker import EncoderWorker


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()


        self.data_original = None
        self.data = None

        self.baseline = np.zeros(3648)
        self.dark = np.zeros(3648)

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
        # # Toolbar 2 - Save
        # # =========================
        self.toolbar_graph_settings.addSeparator()
        self.save_controls = SaveControlsWidget()
        self.toolbar_graph_settings.addWidget(self.save_controls)

        # # =========================
        # # Toolbar 2 - Baseline
        # # =========================
        self.toolbar_graph_settings.addSeparator()
        self.baseline_controls = BaselineControlsWidget()
        self.toolbar_graph_settings.addWidget(self.baseline_controls)

        # # =========================
        # # Toolbar 2 - DARK
        # # =========================
        self.toolbar_graph_settings.addSeparator()
        self.dark_controls = DarkControlsWidget()
        self.toolbar_graph_settings.addWidget(self.dark_controls)


        # # =========================
        # # Toolbar 2 - Motor
        # # =========================
        self.toolbar_graph_settings.addSeparator()
        self.motor_controls = MotorControlsWidget()
        self.toolbar_graph_settings.addWidget(self.motor_controls)

        
        # # =========================
        # # Toolbar 2 - Encoder (angulo)
        # # =========================
        self.toolbar_graph_settings.addSeparator()
        self.encoder_viewer = EncoderViewerWidget()
        self.toolbar_graph_settings.addWidget(self.encoder_viewer)
        
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
        self.scale_controls.scale_clicked.connect(self.scale_function)

        # Save
        self.save_controls.save_clicked.connect(self.save_spectrum)

        #Baseline
        self.baseline_controls.baseline_clicked.connect(self.baseline_offset)

        #Dark
        self.dark_controls.dark_clicked.connect(self.dark_offset)

        # Motor buttons
        self.motor_controls.motor_command.connect(self.motor_worker.send_command)

        # Encoder connections
        self.encoder_thread.started.connect(self.encoder_worker.receber_angulo)
        self.encoder_worker.dados_recebidos.connect(self.encoder_viewer.atualizar_dados)

    def dark_offset(self):
        if len(self.data)>0:
            self.dark = self.data_original.copy()

    def baseline_offset(self):
        print('baseline')
        if len(self.data > 0):
            self.baseline = np.median(self.data_original[0:100])

    def save_spectrum(self):
        print('Salvando')

        caminho_arquivo, _ = QFileDialog.getSaveFileName(
        self,
        "Salvar Arquivo",
        "meu_arquivo.csv",  # Nome padrão que já vem pré-preenchido
        "Arquivos de Texto (*.txt);;Arquivos CSV (*.csv);;Todos os Arquivos (*)",
    )
        if len(self.data)!= 0:
            x = [i for i in range(len(self.data))]
            spectrum = pd.DataFrame({"pixel": x, "intensidade": self.data})
            spectrum.to_csv(caminho_arquivo, index=None)


    def auto_scale_function(self):
        print("Auto scale acionado.")
        self.ccd_graph.enableAutoRange()

    def scale_function(self):
        print("Scale Acionado")
        if len(self.data > 0 ):
            max_value = np.max(self.data)
            self.ccd_graph.setYRange(0, max_value + 100)


    def update_graph(self, data: np.ndarray):
        self.data_original = data.copy()
        self.data = self.data_original - self.baseline - self.dark
        self.curve.setData(self.data)

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

        # =========================
        # Encoder Worker
        # =========================
        self.encoder_thread = QThread()
        self.encoder_worker = EncoderWorker()
        self.encoder_worker.moveToThread(self.encoder_thread)
        self.encoder_thread.started.connect(self.encoder_worker.receber_angulo)
        self.encoder_thread.start()

    def closeEvent(self, event):
        print("Encerrando threads...")
        
        # Para o loop interno do encoder antes de matar a thread
        if hasattr(self, 'encoder_worker'):
            self.encoder_worker.stop()

        for t in [self.ccd_thread, self.motor_thread, self.encoder_thread]:
            if t.isRunning():
                t.quit()
                t.wait()

        print("Threads finalizadas com sucesso.")
        event.accept()


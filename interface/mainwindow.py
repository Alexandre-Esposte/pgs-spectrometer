from PyQt5.QtCore import pyqtSignal, QObject, Qt, QThread, QRunnable, QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QToolBar, QAction
import pyqtgraph as pg
import numpy as np
import sys
from .controlccd import * 
from .controlmotor import *


# =====================================
# Janela Principal da Aplicação
# =====================================
class MainWindow(QMainWindow):
    start_worker = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PGS - Espectrometro (Threaded)")
        self.resize(800, 400)

        # Thread e Worker
        self.sensor_thread = QThread()
        self.worker = CCDWorker(integration_time = 50_000, shots_per_acquisition = 10, dark_correction = True)
        self.worker.moveToThread(self.sensor_thread)
        self.sensor_thread.started.connect(self.worker.start_acquisition)
        self.worker.data_ready.connect(self.atualizar_grafico)
        self.start_worker.connect(self.worker.start_acquisition)

        # Toolbar
        toolbar = QToolBar("Ferramentas")
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        self.botao_iniciar = QAction("Iniciar Aquisição", self)
        self.botao_parar = QAction("Parar Aquisição", self)
        self.botao_motor = QAction("Controle do Motor", self)
        self.botao_config_ccd = QAction("Configurar CCD", self)

        toolbar.addAction(self.botao_iniciar)
        toolbar.addAction(self.botao_parar)
        toolbar.addAction(self.botao_motor)
        toolbar.addAction(self.botao_config_ccd)

        self.botao_iniciar.triggered.connect(self.iniciar_thread_aquisicao)
        self.botao_parar.triggered.connect(self.parar_thread_aquisicao)
        self.botao_motor.triggered.connect(self.abrir_janela_motor)
        self.botao_config_ccd.triggered.connect(self.abrir_janela_config_ccd)

        self.botao_parar.setEnabled(False)

        # Área Central com gráfico
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Intensidade')
        self.plot_widget.setLabel('bottom', 'Pixel')
        self.plot_widget.setTitle('Espectro CCD')

        self.plot_widget.setYRange(0, 1000)

        layout.addWidget(self.plot_widget)
        self.setCentralWidget(central_widget)

        self.curva = self.plot_widget.plot([], [], pen='y')

        QCoreApplication.instance().aboutToQuit.connect(self.clean_up)

    def iniciar_thread_aquisicao(self):
        if not self.sensor_thread.isRunning():
            self.sensor_thread.start()
            self.botao_iniciar.setEnabled(False)
            self.botao_parar.setEnabled(True)

    def parar_thread_aquisicao(self):
        if self.sensor_thread.isRunning():
            self.worker.stop_acquisition()
            if not self.sensor_thread.wait(2000):
                print("Aviso: Thread não encerrou a tempo. Terminando...")
                self.sensor_thread.terminate()
                self.sensor_thread.wait()
            self.botao_iniciar.setEnabled(True)
            self.botao_parar.setEnabled(False)
            print("Thread encerrada.")

    def atualizar_grafico(self, x, y):
        self.curva.setData(x, y)

    def abrir_janela_motor(self):
        self.motor_control = MotorControl(self)
        self.motor_control.show()

    def abrir_janela_config_ccd(self):
        dialog = CCDConfigDialog(self.worker.config, self)
        dialog.exec_()    

    def clean_up(self):
        print("Limpando recursos e parando thread...")
        self.parar_thread_aquisicao()


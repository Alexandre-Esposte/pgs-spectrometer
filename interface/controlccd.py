
from AlphalasCCD import *
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QThread, QRunnable, QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QToolBar, QAction, QDialog, QLabel, QSpinBox, QCheckBox,QVBoxLayout, QHBoxLayout, QPushButton
import time

class CCDWorker(QObject):
    # Sinal que carrega os dados (x, y) para o thread principal
    data_ready = pyqtSignal(list, list)

    def __init__(self, parent=None, integration_time: int = 1000, shots_per_acquisition: int = 1, dark_correction: bool = True):
        super().__init__(parent)
        self._running = False

        self.integration_time = integration_time
        self.shots_per_acquisition = shots_per_acquisition
        self.dark_correction = dark_correction
        self.ccd = AlphalasCCD()
        self.ccd.updateSetting("integration_time", self.integration_time)
        self.ccd.updateSetting("shots_per_acquisition", self.shots_per_acquisition)
        self.ccd.updateSetting('dark_correction',self.dark_correction)

        self.config = CCDConfig()

        # Conecta os sinais para atualizar o hardware em tempo real
        self.config.integration_time_changed.connect(self.update_integration_time)
        self.config.shots_per_acquisition_changed.connect(self.update_shots_per_acquisition)
        self.config.dark_correction_changed.connect(self.update_dark_correction)

    def start_acquisition(self):
        """Método principal que inicia o loop de aquisição de dados."""
        self._running = True
        print("Aquisição de dados iniciada.")
        
        while self._running:
            try:
                # 1. Retreive the data
                data = self.ccd.readoutData()
                # print(f"Dados lidos: {data.shape}")
                
                # 2. Prepara os dados para emissão
                y = list(data)
                x = [xi for xi in range(len(y))]
                
                # 3. Emite o sinal para o thread principal (GUI)
                self.data_ready.emit(x, y)
                
                # Pausa para evitar 100% de uso da CPU e respeitar a taxa de amostragem
                # Note: O tempo de integração já é uma limitação, mas essa pausa
                # garante que o loop não seja excessivamente rápido.
                time.sleep(0.1) 
                
            except Exception as e:
                print(f"Erro durante a aquisição: {e}")
                # Em caso de erro, é bom parar o loop
                self._running = False
            
        print("Aquisição de dados interrompida.")
        
    def stop_acquisition(self):
        """Define a flag para interromper o loop de aquisição."""
        self._running = False

    def update_integration_time(self, value):
        print(f"Atualizando integration_time para {value}")
        self.ccd.updateSetting("integration_time", value)

    def update_shots_per_acquisition(self, value):
        print(f"Atualizando shots_per_acquisition para {value}")
        self.ccd.updateSetting("shots_per_acquisition", value)

    def update_dark_correction(self, value):
        print(f"Atualizando dark_correction para {value}")
        self.ccd.updateSetting("dark_correction", value)
  

class CCDConfig(QObject):
    integration_time_changed = pyqtSignal(int)
    shots_per_acquisition_changed = pyqtSignal(int)
    dark_correction_changed = pyqtSignal(bool)

    def __init__(self, integration_time=1000, shots_per_acquisition=1, dark_correction=True):
        super().__init__()
        self._integration_time = integration_time
        self._shots_per_acquisition = shots_per_acquisition
        self._dark_correction = dark_correction

    @property
    def integration_time(self):
        return self._integration_time

    @integration_time.setter
    def integration_time(self, value):
        if self._integration_time != value:
            self._integration_time = value
            self.integration_time_changed.emit(value)

    @property
    def shots_per_acquisition(self):
        return self._shots_per_acquisition

    @shots_per_acquisition.setter
    def shots_per_acquisition(self, value):
        if self._shots_per_acquisition != value:
            self._shots_per_acquisition = value
            self.shots_per_acquisition_changed.emit(value)

    @property
    def dark_correction(self):
        return self._dark_correction

    @dark_correction.setter
    def dark_correction(self, value):
        if self._dark_correction != value:
            self._dark_correction = value
            self.dark_correction_changed.emit(value)

class CCDConfigDialog(QDialog):
    def __init__(self, config: CCDConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações do CCD")
        self.config = config

        layout = QVBoxLayout(self)

        # integration_time
        layout.addWidget(QLabel("Tempo de Integração (µs):"))
        self.spin_integration = QSpinBox()
        self.spin_integration.setRange(100, 1000000)  # ajuste conforme seu hardware
        self.spin_integration.setValue(self.config.integration_time)
        layout.addWidget(self.spin_integration)

        # shots_per_acquisition
        layout.addWidget(QLabel("Número de shots por aquisição:"))
        self.spin_shots = QSpinBox()
        self.spin_shots.setRange(1, 100)
        self.spin_shots.setValue(self.config.shots_per_acquisition)
        layout.addWidget(self.spin_shots)

        # dark_correction
        self.checkbox_dark = QCheckBox("Correção de Dark")
        self.checkbox_dark.setChecked(self.config.dark_correction)
        layout.addWidget(self.checkbox_dark)

        # Botões OK e Cancelar
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancelar")
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        # Conexões
        self.btn_ok.clicked.connect(self.apply_and_close)
        self.btn_cancel.clicked.connect(self.reject)

    def apply_and_close(self):
        # Atualiza o objeto config, que automaticamente emitirá sinais para o worker
        self.config.integration_time = self.spin_integration.value()
        self.config.shots_per_acquisition = self.spin_shots.value()
        self.config.dark_correction = self.checkbox_dark.isChecked()
        self.accept()
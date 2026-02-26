import time
import numpy as np

from ccd.AlphalasCCD import *
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QTimer

class CCDWorker(QObject):

    data = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()

        self.ccd = AlphalasCCD()

        self.integration_time = 100_000 #1.000.000us -> 100ms
        self.scans_to_average = 1
        self.dark_correction = False

        self.aquisition_frequency = 10#ms
        self.timer = None

        self.update_settings({
            "integration_time": self.integration_time,
            "scans_to_average": self.scans_to_average,
            "dark_correction": self.dark_correction})


    @pyqtSlot()
    def initialize(self):
        self.timer = QTimer(self)  # parent = worker
        self.timer.setInterval(self.aquisition_frequency)  # Convertendo microsegundos para milissegundos
        self.timer.timeout.connect(self._acquire)

        self.timer.start()

    @pyqtSlot()
    def start(self):
         if self.timer and not self.timer.isActive():
            self.timer.start()

    @pyqtSlot()
    def stop(self):
        if self.timer and self.timer.isActive():
            self.timer.stop()


    @pyqtSlot()
    def pause(self):
        if self.timer and self.timer.isActive():
            self.timer.stop()

        
    @pyqtSlot(dict)
    def update_settings(self, settings):

        self.stop()
        time.sleep(2) # Garantindo que o timer foi realmente parado antes de atualizar as configurações
        print(settings)
        self.integration_time = settings["integration_time"]
        self.scans_to_average = settings["scans_to_average"]
        self.dark_correction = settings["dark_correction"]

        self.ccd.updateSetting("integration_time", self.integration_time)
        self.ccd.updateSetting("shots_per_acquisition", self.scans_to_average)
        self.ccd.updateSetting('dark_correction', self.dark_correction)

        self.start()

    def _acquire(self):
                 
        if not self.timer.isActive():
            return

        # Limpando bufffer do ccd
        while self.ccd.device.getQueueStatus() > 0:
            self.ccd.device.read(self.ccd.device.getQueueStatus())

        # Mockando dados do ccd
        # x = np.linspace(0,100, 2048)
        # signal = np.random.uniform(1, 20, size = x.shape) * np.sin(x) + np.random.normal(0, 0.05, size = x.shape)
        signal = self.ccd.readoutData()

        self.data.emit(signal)
            

    


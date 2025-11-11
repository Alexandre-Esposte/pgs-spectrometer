from AlphalasCCD import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import logging


logger = logging.getLogger(__main__)
console_handler = logging.StreamHandler()

console_formatter = logging.Formatter('%(asctime)s - %(levelname)s- %(name)s : %(message)s')
console_handler.setFormatter(console_formatter)
console_handler.setLevel("DEBUG")


logger.addHandler(console_handler)


class WorkerCCD(QObject):

    emissor = pyqtSignal(list, list)

    finished = pyqtSignal()

    def __init__(self, integration_time: int = 1000, shots_per_acquisition: int = 1, dark_correction: bool = True):
        super().__init__()

        self._running = False
        self._thread = None

        self.integration_time = integration_time
        self.shots_per_acquisition = shots_per_acquisition
        self.dark_correction = dark_correction

        self.ccd = AlphalasCCD()
        self.ccd.updateSetting("integration_time", self.integration_time)
        self.ccd.updateSetting("shots_per_acquisition", self.shots_per_acquisition)
        self.ccd.updateSetting('dark_correction',self.dark_correction)

    def run(self):
        """Método principal que inicia o loop de aquisição de dados."""

        self._running = True
        logger.debug("Aquisição de dados iniciada.")
        
        while self._running:
            try:
                # 1. Retreive the data
                data = self.ccd.readoutData()
                
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
                logger.error(f"Erro durante a aquisição: {e}")
                # Em caso de erro, é bom parar o loop
                self._running = False
            
        logger.debug("Aquisição de dados finalizada.")

    def start(self):
        """Inicializa captura do ccd"""
        self._running = True
        self.run()

    def stop(self):
        """Finaliza captura do ccd"""
        self._running = False
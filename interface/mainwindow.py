from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QToolBar, QAction
import pyqtgraph as pg
import numpy as np
import sys

# =====================================
# Classe que simula o sensor (emite sinal com dados)
# =====================================
class Sensor(QObject):
    # define um sinal que carrega os dados (x, y)
    data_ready = pyqtSignal(np.ndarray, np.ndarray)

    def emitir_dados(self):
        """Simula envio de dados"""
        x = np.linspace(0, 1, 2000) + np.random.normal(0,2)
        y = np.sin(2 * np.pi * 10 * x) 
        self.data_ready.emit(x, y)  # emite o sinal com os dados


# =====================================
# Janela principal
# =====================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PGS - Espectrometro")
        self.resize(800, 400)

        # ---------- TOOLBAR ----------
        toolbar = QToolBar("Ferramentas")
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Exemplo de botões
        botao_iniciar = QAction("Iniciar", self)
        botao_parar = QAction("Parar", self)
        toolbar.addAction(botao_iniciar)
        toolbar.addAction(botao_parar)

        # ---------- ÁREA CENTRAL ----------
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        self.setCentralWidget(central_widget)

        # Cria uma referência à curva (para atualizar depois)
        self.curva = self.plot_widget.plot([], [])

        # ---------- SENSOR ----------
        self.sensor = Sensor()
        self.sensor.data_ready.connect(self.atualizar_grafico)

        # Liga o botão para simular aquisição de dados
        botao_iniciar.triggered.connect(self.sensor.emitir_dados)

    # Slot que atualiza o gráfico quando chegam novos dados
    def atualizar_grafico(self, x, y):
        self.curva.setData(x, y)


# =====================================
# Execução do app
# =====================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

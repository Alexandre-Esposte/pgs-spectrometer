import serial
import struct
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QSlider, QRadioButton, QGroupBox
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QThread, QRunnable, QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QToolBar, QAction
import time

# =====================================
# Janela de Controle do Motor de Passo
# =====================================
class MotorControl(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Controle Manual do Motor de Passo")
        self.setFixedSize(400, 200)

        # Porta padrão
        self.porta_serial = "/dev/ttyACM0"  # Altere se necessário

        # Interface
        self.label_status = QLabel("Status: Conectando...")
        self.label_velocidade = QLabel("Tempo entre passos: 100 ms")

        self.slider_velocidade = QSlider(Qt.Horizontal)
        self.slider_velocidade.setMinimum(3)
        self.slider_velocidade.setMaximum(255)
        self.slider_velocidade.setValue(100)

        self.instrucao = QLabel(
            "← Diminuir ângulo | → Aumentar ângulo | espaço Parar\n↑↓ Ajusta tempo entre passos"
        )

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_status)
        layout.addWidget(self.label_velocidade)
        layout.addWidget(self.slider_velocidade)
        layout.addWidget(self.instrucao)
        self.setLayout(layout)

        # Serial
        self.serial_conn = None
        self.conectar_serial()

        # Foco para capturar teclas
        self.setFocusPolicy(Qt.StrongFocus)

    def conectar_serial(self):
        try:
            self.serial_conn = serial.Serial(self.porta_serial, 115200, timeout=1)
            time.sleep(0.1)
            self.label_status.setText(f"Conectado em {self.porta_serial}")
        except Exception as e:
            self.label_status.setText(f"Erro: {e}")
            print(f"[Erro] Conexão serial: {e}")

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Left:
            print("← Diminuir ângulo")
            self.enviar_comando(sentido=0)
        elif key == Qt.Key_Right:
            print("→ Aumentar ângulo")
            self.enviar_comando(sentido=1)
        elif key == Qt.Key_Space:
            print("␣ Parar")
            self.enviar_comando(status=0)
        elif key == Qt.Key_Up:
            valor = self.slider_velocidade.value()
            novo = min(255, valor + 5)
            self.slider_velocidade.setValue(novo)
            print(f"↑ Velocidade aumentada: {novo}ms")
            self.label_velocidade.setText(f'Tempo entre passos: {novo} ms')
        elif key == Qt.Key_Down:
            valor = self.slider_velocidade.value()
            novo = max(3, valor - 5)
            self.slider_velocidade.setValue(novo)
            print(f"↓ Velocidade diminuída: {novo}ms")
            self.label_velocidade.setText(f'Tempo entre passos: {novo} ms')
        else:
            super().keyPressEvent(event)

    def enviar_comando(self, sentido=None, status=1):
        if self.serial_conn and self.serial_conn.is_open:
            try:
                SYNC_BYTE = 0xAA
                sentido_val = sentido if sentido is not None else 0
                status_val = status
                tempo_val = self.slider_velocidade.value()

                data = struct.pack('<BBB', sentido_val, status_val, tempo_val)
                self.serial_conn.write(bytes([SYNC_BYTE]))
                self.serial_conn.write(data)
                self.serial_conn.flush()

                print(f"Comando enviado: {[hex(SYNC_BYTE)] + [hex(b) for b in data]}")
            except Exception as e:
                print(f"[Erro] ao enviar comando: {e}")
        else:
            print("[Aviso] Serial não conectada.")

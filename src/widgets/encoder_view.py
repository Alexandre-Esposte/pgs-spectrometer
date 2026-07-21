from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal

class EncoderViewerWidget(QWidget):
    # Sinal caso você queira avisar a MainWindow que o encoder foi zerado
    encoder_reset = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.angulo_rede = 20.0

        # Layout principal horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)

        # Estilização de rótulo para destaque
        self.label_titulo = QLabel("Encoder:")
        self.label_titulo.setStyleSheet("font-weight: bold;")

        # Display do Ângulo (usando um QFrame ou Label estilizado)
        self.angle_display = QLabel(f"{self.angulo_rede}°")
        self.angle_display.setAlignment(Qt.AlignCenter)
        self.angle_display.setMinimumWidth(100)
        self.angle_display.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #00ff00;
                font-family: 'Consolas', monospace;
                font-size: 18px;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px;
            }
        """)

        # Display de Pulsos (menor, apenas informativo)
        self.pulse_display = QLabel("Pulsos: 0")
        self.pulse_display.setStyleSheet("color: #888; font-size: 11px;")

        # Botão de Reset/Zerar
        self.reset_button = QPushButton("Zerar")
        self.reset_button.setFixedWidth(60)
        self.reset_button.clicked.connect(self._handle_reset)

        # Montagem do Layout
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.angle_display)
        
        # Container vertical para info secundária
        layout.addWidget(self.pulse_display)
        
        layout.addStretch() # Empurra tudo para a esquerda
        layout.addWidget(self.reset_button)

    @pyqtSlot(int, int)
    def atualizar_dados(self, deltapassos, totalabsoluto):
        """
        Slot para receber os dados vindos do EncoderWorker.
        """
        print(deltapassos, totalabsoluto)
        variação_angular_rede = deltapassos / 4876
        self.angulo_rede = self.angulo_rede + variação_angular_rede
        self.angle_display.setText(f"{self.angulo_rede:.2f}°")
        self.pulse_display.setText(f"Pulsos: {totalabsoluto}")

    def _handle_reset(self):
        """
        Ação ao clicar no botão zerar. 
        Aqui você pode emitir um sinal para que o Worker envie um comando 
        de zerar para o ESP32, se houver suporte.
        """
        self.angle_display.setText("0.00°")
        self.pulse_display.setText("Pulsos: 0")
        self.encoder_reset.emit()
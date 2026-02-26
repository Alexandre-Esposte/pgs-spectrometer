from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSpinBox, QComboBox, QFrame, QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon

class MotorControlsWidget(QWidget):
    motor_command = pyqtSignal(dict)

    def __init__(self, parent = None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.spin_velocity = QSpinBox()
        self.spin_velocity.setRange(3,255)

        self.combobox_direction = QComboBox()
        self.combobox_direction.addItems(['diminuir angulo','aumentar angulo'])

        self.btn_start = QPushButton("Acionar motor")
        self.btn_start.setIcon(QIcon("icons/start.png"))

        self.btn_stop  = QPushButton("Parar motor")
        self.btn_stop.setIcon(QIcon("icons/stop.png"))

        layout.addWidget(QLabel('Tempo de acionamento entre as bobinas:'))
        layout.addWidget(self.spin_velocity)
        layout.addWidget(self.combobox_direction)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)

        # Conectando botoes
        self.btn_start.clicked.connect(self._emit_settings_start)
        self.btn_stop.clicked.connect(self._emit_settings_stop)

    def _emit_settings_start(self):
        velocity = self.spin_velocity.value()
        direction = self.combobox_direction.currentText()

        if direction == "diminuir angulo":
            direction = 0
        else:
            direction = 1

        status = 1

        settings = {
            "velocity": velocity,
            'direction': direction,
            'status': status
        }
        self.motor_command.emit(settings)

    def _emit_settings_stop(self):
        velocity = self.spin_velocity.value()
        direction = self.combobox_direction.currentText()

        if direction == "diminuir angulo":
            direction = 0
        else:
            direction = 1

        status = 0

        settings = {
            "velocity": velocity,
            'direction': direction,
            'status': status
        }

        self.motor_command.emit(settings)
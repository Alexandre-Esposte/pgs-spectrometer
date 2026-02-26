from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel,
    QSpinBox, QComboBox, QCheckBox, QPushButton
)
from PyQt5.QtCore import pyqtSignal


class CCDSettingsWidget(QWidget):

    settings_applied = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.dark_checkbox = QCheckBox("Dark Correction")

        self.integration_spin = QSpinBox()
        self.integration_spin.setRange(1, 60_000_000)

        self.ordem = QComboBox()
        self.ordem.addItems(["s", "ms", "us"])

        self.average_spin = QSpinBox()
        self.average_spin.setRange(1, 100)

        self.apply_button = QPushButton("Aplicar")

        layout.addWidget(self.dark_checkbox)
        layout.addWidget(QLabel("Integration Time:"))
        layout.addWidget(self.integration_spin)
        layout.addWidget(self.ordem)
        layout.addWidget(QLabel("Scans to Average :"))
        layout.addWidget(self.average_spin)
        layout.addWidget(self.apply_button)

        # Conectando botão
        self.apply_button.clicked.connect(self._emit_settings)

    def _emit_settings(self):

        integration = self.integration_spin.value()
        ordem = self.ordem.currentText()

        if ordem == "s":
            integration *= 1e6
            integration = int(integration)
        elif ordem == "ms":
            integration *= 1e3
            integration = int(integration)
        elif ordem == "us":
            integration *= 1
            integration = int(integration)

        settings = {
            "integration_time": integration,
            "scans_to_average": self.average_spin.value(),
            "dark_correction": self.dark_checkbox.isChecked(),
        }

        self.settings_applied.emit(settings)

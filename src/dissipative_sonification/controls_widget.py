"""Parameter control panel for the Dissipative Sonification studio.

Provides sliders / value boxes for the Gray-Scott equation parameters
(feed and kill) plus Pause and Reset buttons. Changes are pushed directly
onto the shared simulation object; the pipeline timer reads them each tick.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QDoubleSpinBox,
)

from dissipative_sonification.simulation import GrayScott
from dissipative_sonification import config as cfg


class ControlsWidget(QWidget):
    pause_requested = Signal(bool)
    reset_requested = Signal()

    _SCALE = 10000  # slider int resolution

    def __init__(self, sim: GrayScott, parent=None):
        super().__init__(parent)
        self.sim = sim

        form = QFormLayout(self)

        self.spin_f = QDoubleSpinBox()
        self.spin_f.setRange(0.005, 0.12)
        self.spin_f.setSingleStep(0.001)
        self.spin_f.setDecimals(4)
        self.spin_f.setValue(self.sim.f)
        self.spin_f.valueChanged.connect(self._on_f)

        self.slider_f = QSlider(Qt.Horizontal)
        self.slider_f.setRange(50, 1200)
        self.slider_f.setValue(int(self.sim.f * self._SCALE))
        self.slider_f.valueChanged.connect(self._on_f_slider)

        self.spin_k = QDoubleSpinBox()
        self.spin_k.setRange(0.01, 0.09)
        self.spin_k.setSingleStep(0.001)
        self.spin_k.setDecimals(4)
        self.spin_k.setValue(self.sim.k)
        self.spin_k.valueChanged.connect(self._on_k)

        self.slider_k = QSlider(Qt.Horizontal)
        self.slider_k.setRange(100, 900)
        self.slider_k.setValue(int(self.sim.k * self._SCALE))
        self.slider_k.valueChanged.connect(self._on_k_slider)

        f_row = QHBoxLayout()
        f_row.addWidget(self.slider_f)
        f_row.addWidget(self.spin_f)

        k_row = QHBoxLayout()
        k_row.addWidget(self.slider_k)
        k_row.addWidget(self.spin_k)

        form.addRow(QLabel("Feed f"), f_row)
        form.addRow(QLabel("Kill k"), k_row)

        btn_row = QHBoxLayout()
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setCheckable(True)
        self.btn_pause.toggled.connect(self._on_pause)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self._on_reset)
        btn_row.addWidget(self.btn_pause)
        btn_row.addWidget(self.btn_reset)
        btn_row.addStretch(1)
        form.addRow(btn_row)

    # ------------------------------------------------------------------ #
    def _on_f(self, value):
        self.sim.f = value
        self.slider_f.blockSignals(True)
        self.slider_f.setValue(int(value * self._SCALE))
        self.slider_f.blockSignals(False)

    def _on_f_slider(self, value):
        self.spin_f.setValue(value / self._SCALE)

    def _on_k(self, value):
        self.sim.k = value
        self.slider_k.blockSignals(True)
        self.slider_k.setValue(int(value * self._SCALE))
        self.slider_k.blockSignals(False)

    def _on_k_slider(self, value):
        self.spin_k.setValue(value / self._SCALE)

    def _on_pause(self, checked):
        self.pause_requested.emit(checked)
        self.btn_pause.setText("Resume" if checked else "Pause")

    def _on_reset(self):
        self.reset_requested.emit()

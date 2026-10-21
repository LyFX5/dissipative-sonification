"""Main Qt window for the Dissipative Sonification studio.

Layout: a horizontal splitter.
  - Left:  GrayScott reaction-diffusion matrix (custom QPainter widget),
           supports mouse-scrub painting of concentration.
  - Right: vertical stack of (top) animated matplotlib plots and
           (bottom) parameter control panel.

A single QTimer drives the whole pipeline each tick: simulation step ->
metric extraction -> audio state push -> matrix repaint -> plot update.
The audio engine runs on its own PortAudio callback thread.
"""

import datetime

import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from dissipative_sonification.simulation import GrayScott
from dissipative_sonification.sonification import AudioEngine
from dissipative_sonification.matrix_widget import MatrixWidget
from dissipative_sonification.plots_widget import PlotsWidget
from dissipative_sonification.controls_widget import ControlsWidget
from dissipative_sonification import config as cfg


class QApp(QMainWindow):
    FPS = 30
    INTERVAL_MS = int(1000 / FPS)

    STEPS_PER_FRAME = 10

    def __init__(self, sim: GrayScott = None, audio: AudioEngine = None):
        super().__init__()
        self.sim = sim or GrayScott()
        self.audio = audio or AudioEngine()

        self.setWindowTitle("Dissipative Structures · Study Studio")
        self.resize(1280, 800)

        # Left: interactive matrix scene
        self.matrix = MatrixWidget(self.sim)

        # Right: plots on top, controls on bottom
        self.plots = PlotsWidget(self.sim)
        self.controls = ControlsWidget(self.sim)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        right_layout.addWidget(self.plots, stretch=3)
        right_layout.addWidget(self.controls, stretch=1)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.matrix)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([620, 620])
        self.setCentralWidget(splitter)

        # Pause/resume & reset coordination (also toggled by control panel)
        self.controls.pause_requested.connect(self.set_paused)
        self.controls.reset_requested.connect(self.reset)

        # Main pipeline timer
        self._timer = QTimer(self)
        self._timer.setInterval(self.INTERVAL_MS)
        self._timer.timeout.connect(self._tick)
        self.paused = False

    # ------------------------------------------------------------------ #
    # Control
    # ------------------------------------------------------------------ #
    def set_paused(self, paused: bool):
        self.paused = paused
        if paused:
            self._timer.stop()
        else:
            self._timer.start()

    def reset(self):
        self.sim.reset()
        self.plots.reset()

    # ------------------------------------------------------------------ #
    # Pipeline
    # ------------------------------------------------------------------ #
    def _tick(self):
        if self.paused:
            return
        for _ in range(self.STEPS_PER_FRAME):
            self.sim.step()
        self.sim.apply_paint()
        metrics = self.sim.get_metrics()
        self.audio.update_state(metrics)
        self.matrix.update_frame()
        self.plots.update_frame(metrics)

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def start(self):
        self.audio.start()
        self._timer.start()

    def shutdown(self):
        self._timer.stop()
        self.audio.stop()

"""Animated monitoring plots for the Dissipative Sonification studio.

Hosts a matplotlib figure (rendered via Qt's FigureCanvasQTAgg) with four
subplots that evolve with the simulation:
  - Energy  (mean U + mean V over time)
  - Entropy (Shannon entropy over time)
  - Concentrations (mean U and mean V curves)
  - Phase plane (trajectory dot in (mean V, entropy) space with faint trail)

Rather than rebuilding the figure each tick, we keep ring buffers and update
the artists' data in place for speed.
"""

from collections import deque

import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget, QVBoxLayout


class PlotsWidget(QWidget):
    TRAIL = 240  # number of samples kept for each curve

    def __init__(self, sim, parent=None):
        super().__init__(parent)
        self.sim = sim
        self._t = deque(maxlen=self.TRAIL)
        self._energy = deque(maxlen=self.TRAIL)
        self._entropy = deque(maxlen=self.TRAIL)
        self._u = deque(maxlen=self.TRAIL)
        self._v = deque(maxlen=self.TRAIL)

        self.fig, self.axes = plt.subplots(
            2, 2, figsize=(6.4, 4.8), dpi=100
        )
        self.fig.subplots_adjust(left=0.12, right=0.96, bottom=0.12,
                                 top=0.92, wspace=0.33, hspace=0.45)

        ax_e, ax_s, ax_c, ax_p = self.axes.flat

        self.line_energy, = ax_e.plot([], [], color="#4cc9f0", lw=1.2)
        ax_e.set_title("Energy")
        ax_e.set_ylabel("mean U+V")

        self.line_entropy, = ax_s.plot([], [], color="#f72585", lw=1.2)
        ax_s.set_title("Entropy")
        ax_s.set_ylabel("bits")

        self.line_u, = ax_c.plot([], [], color="#90be6d", lw=1.0)
        self.line_v, = ax_c.plot([], [], color="#f9c74f", lw=1.0)
        ax_c.set_title("Concentrations")
        ax_c.set_ylabel("mean U / V")

        ax_p.set_title("Phase plane")
        ax_p.set_xlabel("mean V")
        ax_p.set_ylabel("entropy")
        self._trail = ax_p.plot([], [], color="#9b5de5", lw=0.7, alpha=0.4)[0]
        self._dot = ax_p.plot([], [], "o", color="#f15bb5", ms=5)[0]

        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        # Light theme
        self.fig.patch.set_facecolor("#fafafa")
        for ax in self.axes.flat:
            ax.set_facecolor("#fafafa")

    # ------------------------------------------------------------------ #
    def reset(self):
        for buf in (self._t, self._energy, self._entropy,
                    self._u, self._v):
            buf.clear()
        for artist in (self.line_energy, self.line_entropy,
                       self.line_u, self.line_v, self._trail, self._dot):
            artist.set_data([], [])
        for ax in self.axes.flat:
            ax.relim()
            ax.autoscale_view()
        self.canvas.draw_idle()

    def update_frame(self, metrics):
        t = (self._t[-1] + 1.0) if self._t else 0.0
        u_mean = float(np.mean(self.sim.U))
        v_mean = float(np.mean(self.sim.V))

        self._t.append(t)
        self._energy.append(u_mean + v_mean)
        self._entropy.append(metrics["entropy"])
        self._u.append(u_mean)
        self._v.append(v_mean)

        ts = np.asarray(self._t)
        self.line_energy.set_data(ts, np.asarray(self._energy))
        self.line_entropy.set_data(ts, np.asarray(self._entropy))
        self.line_u.set_data(ts, np.asarray(self._u))
        self.line_v.set_data(ts, np.asarray(self._v))
        self._dot.set_data([v_mean], [metrics["entropy"]])

        trail_v = np.asarray(self._v)
        trail_s = np.asarray(self._entropy)
        self._trail.set_data(trail_v, trail_s)

        for ax in (self.axes[0, 0], self.axes[0, 1],
                   self.axes[1, 0], self.axes[1, 1]):
            ax.relim()
        for ax, line in ((self.axes[0, 0], self.line_energy),
                         (self.axes[0, 1], self.line_entropy),
                         (self.axes[1, 0], self.line_u)):
            ax.autoscale_view()

        ax_p = self.axes[1, 1]
        ax_p.set_xlim(0.0, max(0.6, float(np.max(self._v)) * 1.1))
        ax_p.set_ylim(0.0, max(1.0, float(np.max(self._entropy)) * 1.1))

        self.canvas.draw_idle()

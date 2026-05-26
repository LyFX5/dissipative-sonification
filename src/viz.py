import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button
import numpy as np
from .simulation import GrayScott
from .sonification import AudioEngine
from . import config as cfg

class Visualizer:
    def __init__(self, sim: GrayScott, audio: AudioEngine):
        self.sim = sim
        self.audio = audio
        self.paused = False
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.fig.subplots_adjust(bottom=0.25)

        # Image display
        self.im = self.ax.imshow(self.sim.V, cmap='inferno', vmin=0, vmax=1, aspect='equal')
        self.ax.set_title("Dissipative Structures: Reaction-Diffusion Sonification")
        self.ax.axis('off')

        # Controls
        ax_f = plt.axes([0.25, 0.15, 0.65, 0.03])
        ax_k = plt.axes([0.25, 0.10, 0.65, 0.03])
        ax_btn = plt.axes([0.8, 0.02, 0.15, 0.05])

        self.slider_f = Slider(ax_f, 'Feed (f)', 0.01, 0.12, valinit=cfg.DEFAULT_F)
        self.slider_k = Slider(ax_k, 'Kill (k)', 0.02, 0.09, valinit=cfg.DEFAULT_K)
        self.btn_pause = Button(ax_btn, '⏸ Pause')

        self.slider_f.on_changed(self._update_f)
        self.slider_k.on_changed(self._update_k)
        self.btn_pause.on_clicked(self._toggle_pause)

        self.ani = animation.FuncAnimation(
            self.fig, self._update, interval=50, blit=False, cache_frame_data=False
        )

    def _update_f(self, val): self.sim.f = val
    def _update_k(self, val): self.sim.k = val

    def _toggle_pause(self, event):
        self.paused = not self.paused
        self.btn_pause.label.set_text("▶ Resume" if self.paused else "⏸ Pause")
        if not self.paused:
            self.ani.event_source.start()
        else:
            self.ani.event_source.stop()

    def _update(self, frame):
        if not self.paused:
            self.sim.step()
            metrics = self.sim.get_metrics()
            self.audio.update_state(metrics)
            self.im.set_data(self.sim.V)
        return [self.im]

    def run(self):
        self.audio.start()
        try:
            plt.show()
        finally:
            self.audio.stop()

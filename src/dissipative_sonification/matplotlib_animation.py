import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dissipative_sonification.simulation import GrayScott


class Visualizer:
    def __init__(self, sim: GrayScott):
        self.sim = sim

        self.steps_per_frame = 10

        self.paused = False

        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.fig.subplots_adjust(bottom=0.25)

        # Image display
        self.im = self.ax.imshow(
            self.sim.V, cmap="inferno", vmin=0, vmax=1, aspect="equal"
        )
        self.ax.set_title(
            "Dissipative Structures: Reaction-Diffusion Sonification"
        )
        self.ax.axis("off")

        self.ani = animation.FuncAnimation(
            self.fig,
            self._update,
            # frames=FRAMES_NUMBER,
            # interval=5,
            blit=False,
            cache_frame_data=False,
        )

    def _update(self, frame):
        if not self.paused:
            for _ in range(self.steps_per_frame):
                self.sim.step()
            self.im.set_data(self.sim.V)
        return [self.im]

    def run(self):
        plt.show()

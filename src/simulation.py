import numpy as np

# from scipy.ndimage import gaussian_filter

import config as cfg


class GrayScott:
    def __init__(self, width=cfg.WIDTH, height=cfg.HEIGHT):
        self.width, self.height = width, height
        self.U = np.ones((height, width), dtype=np.float32)
        self.V = np.zeros((height, width), dtype=np.float32)
        self.f = cfg.DEFAULT_F
        self.k = cfg.DEFAULT_K
        self._seed()

    def _seed(self):
        """Drop initial catalyst patch"""
        cx, cy = self.width // 2, self.height // 2
        self.V[cy - 3 : cy + 3, cx - 3 : cx + 3] = 1.0
        self.U[cy - 3 : cy + 3, cx - 3 : cx + 3] = 0.5

    def step(self):
        """Single reaction-diffusion step with periodic boundaries"""
        lap_U = (
            np.roll(self.U, 1, axis=0)
            + np.roll(self.U, -1, axis=0)
            + np.roll(self.U, 1, axis=1)
            + np.roll(self.U, -1, axis=1)
            - 4 * self.U
        )
        lap_V = (
            np.roll(self.V, 1, axis=0)
            + np.roll(self.V, -1, axis=0)
            + np.roll(self.V, 1, axis=1)
            + np.roll(self.V, -1, axis=1)
            - 4 * self.V
        )

        reaction = self.U * self.V**2
        self.U += cfg.DT * (cfg.DU * lap_U - reaction + self.f * (1 - self.U))
        self.V += cfg.DT * (
            cfg.DV * lap_V + reaction - (self.f + self.k) * self.V
        )

        # Clamp to physical bounds
        np.clip(self.U, 0.0, 1.0, out=self.U)
        np.clip(self.V, 0.0, 1.0, out=self.V)

    def get_metrics(self):
        """Extract sonification-relevant features"""
        v_mean = np.mean(self.V)
        v_row = self.V[self.height // 2, :]  # horizontal scan line for pitch

        # Entropy (Shannon)
        hist, _ = np.histogram(self.V, bins=32, range=(0, 1))
        prob = hist[hist > 0] / hist.sum()
        entropy = -np.sum(prob * np.log2(prob + 1e-12)) / np.log2(
            32
        )  # normalized [0,1]

        # Gradient magnitude (edge detection)
        grad_x = np.diff(self.V, axis=1)
        grad_y = np.diff(self.V, axis=0)
        grad_norm = np.sqrt(np.mean(grad_x**2) + np.mean(grad_y**2))

        # Spatial centroid (x-position of active structure)
        total_mass = np.sum(self.V)
        cx = np.sum(self.V * np.arange(self.width)) / (total_mass + 1e-12)
        pan = (cx / self.width) * 2 - 1  # [-1, 1]

        return {
            "f": self.f,
            "k": self.k,
            "v_mean": v_mean,
            "v_row": v_row,
            "entropy": entropy,
            "gradient": np.clip(grad_norm, 0, 1),
            "pan": pan,
        }

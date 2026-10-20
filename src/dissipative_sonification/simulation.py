import numpy as np

"""
# 1. Rolls
f = 0.04
k = 0.06
f = 0.037
k = 0.06

# 2. Spots
f = 0.014
k = 0.054

# 3. Solitons
f = 0.03
k = 0.062

# 4. Pulsating Solitons
f = 0.025
k = 0.06

# 4. Waves
f = 0.014
k = 0.045

# 5. Mazes
f = 0.029
k = 0.057
"""


class GrayScott:
    def __init__(self, f=0.014, k=0.054):

        grid_size = 256

        self.DU = 0.16
        self.DV = 0.08

        self.dt = 1.0

        self.width, self.height = grid_size, grid_size

        self.U = np.ones((self.height, self.width), dtype=np.float32)
        self.V = np.zeros((self.height, self.width), dtype=np.float32)

        self.initial_condition_type = "drop"

        self.f = f
        self.k = k

        self._seed()

    def reset(self):
        """Re-initialize fields and clear any painted concentration."""
        self.U[...] = 1.0
        self.V[...] = 0.0
        # self.paint_U[...] = 0.0
        # self.paint_V[...] = 0.0
        self._seed()

    def _drop_IC(self):
        """Drop initial catalyst patch"""
        cx, cy = self.width // 2, self.height // 2
        self.U[cy - 3 : cy + 3, cx - 3 : cx + 3] = 0.5
        self.V[cy - 3 : cy + 3, cx - 3 : cx + 3] = 0.25

    def _seed(self):

        if self.initial_condition_type == "trefethen":
            self._trefethen_IC()
        elif self.initial_condition_type == "random":
            self._random_IC()
        elif self.initial_condition_type == "drop":
            self._drop_IC()
        else:
            raise RuntimeError(
                f"Unknown initial condition type: `{self.initial_condition_type}`"
            )

        # populate ghost cells (periodicity)
        self.update_ghosts(self.U)
        self.update_ghosts(self.V)

    def add_brush(
        self,
        x,
        y,
        radius,
        d_u,
        d_v,
    ):
        """Accumulate a concentration bump centred at grid cell (x, y).

        The bump is stored in the paint buffers and merged into the field
        once per tick by :meth:`apply_paint`. Both fields are clamped to
        their physical range.
        """
        ...

    def apply_paint(self):
        """Merge accumulated paint into the field and decay it out."""
        ...

    def step(self):

        # internal domain
        u_center = self.U[1:-1, 1:-1]
        v_center = self.V[1:-1, 1:-1]

        # advance state (Euler step)
        uv2 = u_center * np.power(v_center, 2)
        u_center += self.dt * (
            self.DU * self.laplacian(self.U) - uv2 + self.f * (1 - u_center)
        )
        v_center += self.dt * (
            self.DV * self.laplacian(self.V)
            + uv2
            - (self.f + self.k) * v_center
        )

        # update ghost cells
        self.update_ghosts(self.U)
        self.update_ghosts(self.V)

    @staticmethod
    def laplacian(a, h=1):
        """
        Discretization of Laplacian operator

        Arguments:
            a: 2D array
        """
        return (
            a[2:, 1:-1]
            + a[1:-1, 2:]
            + a[0:-2, 1:-1]
            + a[1:-1, 0:-2]
            - 4 * a[1:-1, 1:-1]
        ) * (1 / h**2)

    @staticmethod
    def update_ghosts(v):
        """
        Apply periodic boundary conditions

        Arguments:
            v: 2D array
        """
        v[0, :] = v[-2, :]
        v[:, 0] = v[:, -2]
        v[-1, :] = v[1, :]
        v[:, -1] = v[:, 1]

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

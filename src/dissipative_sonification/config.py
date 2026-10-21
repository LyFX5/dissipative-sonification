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

# 6. ...
f = 0.0181
k = 0.0540
"""


# === Simulation Parameters ===
WIDTH, HEIGHT = 128, 128

DT = 1.0

DU = 0.16
DV = 0.8

"""
OR
DU = 1.0
DV = 0.5

Fo = 0.8

DX = np.sqrt(DT * 4 * max(DU, DV) / Fo)
"""

DEFAULT_F = 0.055
DEFAULT_K = 0.062

# === Audio Parameters ===
SAMPLE_RATE = 44100
FRAME_SIZE = 1024
MAX_VOICES = 8

# === Musical Mapping ===
# Dorian-mode scale degrees (relative to base)
SCALE_DEGREES = np.array([0, 2, 3, 5, 7, 9, 10, 12])
BASE_FREQ = 65.41  # C2
MIN_FREQ = BASE_FREQ
MAX_FREQ = BASE_FREQ * 4  # C4

# === Mapping Ranges ===
F_TEMPO_MIN, F_TEMPO_MAX = 40, 180  # BPM
K_FILTER_MIN, K_FILTER_MAX = 200, 18000  # Hz
ENTROPY_NOISE_MIN, ENTROPY_NOISE_MAX = -60, -10  # dB
GRADIENT_DIST_MIN, GRADIENT_DIST_MAX = 0.0, 0.8  # saturation index

# === Interactive Painting (brush) ===
BRUSH_RADIUS = 2.0  # grid cells
BRUSH_CONC_U = -0.4  # delta added to U per tick within brush
BRUSH_CONC_V = 0.6  # delta added to V per tick within brush
BRUSH_DECAY = 0.99  # per-tick decay of any residual painted amount

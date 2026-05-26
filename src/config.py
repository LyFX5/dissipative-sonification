import numpy as np

# === Simulation Parameters ===
WIDTH, HEIGHT = 128, 128
DT = 1.0
DU = 1.0
DV = 0.5
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
F_TEMPO_MIN, F_TEMPO_MAX = 40, 180          # BPM
K_FILTER_MIN, K_FILTER_MAX = 200, 18000     # Hz
ENTROPY_NOISE_MIN, ENTROPY_NOISE_MAX = -60, -10  # dB
GRADIENT_DIST_MIN, GRADIENT_DIST_MAX = 0.0, 0.8  # saturation index

import numpy as np
import sounddevice as sd
import threading
from dissipative_sonification import config as cfg


class AudioEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = {
            "f": cfg.DEFAULT_F,
            "k": cfg.DEFAULT_K,
            "v_mean": 0.0,
            "v_row": np.zeros(cfg.WIDTH),
            "v_col": np.zeros(cfg.HEIGHT),
            "v_means_of_cols": np.zeros(cfg.WIDTH),
            "v_maxs_of_cols": np.zeros(cfg.WIDTH),
            "entropy": 0.0,
            "gradient": 0.0,
            "pan": 0.0,
        }
        self._phases = np.zeros(cfg.MAX_VOICES)
        self._active = False
        self._stream = None
        self._buffer = np.zeros((cfg.FRAMES_BLOCK_SIZE, 2))  # pre-allocate

    def update_state(self, new_state: dict):
        with self.lock:
            self.state.update(new_state)

    def resize_array(self, arr: np.ndarray, new_length: int) -> np.ndarray:
        """Resample a 1D array to a new length using linear interpolation,
        covering the same value range (endpoints preserved)."""
        arr = np.asarray(arr)
        old_length = arr.shape[0]
        if old_length == new_length:
            return arr.copy()
        # Old and new sample positions, both spanning [0, 1]
        old_pos = np.linspace(0.0, 1.0, old_length)
        new_pos = np.linspace(0.0, 1.0, new_length)
        return np.interp(new_pos, old_pos, arr)

    def _callback(self, outdata, frames, time, status):
        if status:
            print(f"⚠️ Audio callback status: {status}")
        with self.lock:
            f, k = self.state["f"], self.state["k"]
            v_mean = self.state["v_mean"]
            v_row = self.state["v_row"]
            v_col = self.state["v_col"]
            v_means_of_cols = self.state["v_means_of_cols"]
            v_maxs_of_cols = self.state["v_maxs_of_cols"]
            entropy = self.state["entropy"]
            # gradient = self.state["gradient"]
            pan = self.state["pan"]

        """
        t = np.linspace(0, frames / cfg.SAMPLE_RATE, frames, endpoint=False)
        amp = 0.4
        freq = 100000 * f
        outdata[:, 0] = amp * np.sin(2 * np.pi * freq * t)
        outdata[:, 1] = outdata[:, 0] * 0.8

        v_row_resized = self.resize_array(v_row, frames)
        v_col_resized = self.resize_array(v_col, frames)
        v_means_of_cols_resized = self.resize_array(v_means_of_cols, frames)
        """
        v_maxs_of_cols_resezed = self.resize_array(v_maxs_of_cols, frames)

        outdata[:, 0] = v_maxs_of_cols_resezed * 0.8
        outdata[:, 1] = v_maxs_of_cols_resezed * 0.8

        """
        current_time = time.currentTime
        if int(current_time) % 10 == 0:
            print(f"{current_time=}")
            print(f"{v_row=}")
            print(f"{v_row_resized=}")
            print(f"{outdata=}")
            print()
        """

        """
        # 1. Tempo/Event Rate → probability of triggering notes this frame
        bpm = cfg.F_TEMPO_MIN + (
            15.0 * f * (cfg.F_TEMPO_MAX - cfg.F_TEMPO_MIN)
        )
        event_prob = bpm / 60.0 / (cfg.SAMPLE_RATE / cfg.FRAMES_BLOCK_SIZE)
        trigger = np.random.random() < event_prob

        # 2. Map V-row to frequencies (quantized to scale)
        freqs = np.zeros(cfg.MAX_VOICES)
        amps = np.zeros(cfg.MAX_VOICES)
        if trigger:
            idx = np.random.randint(0, len(v_row), cfg.MAX_VOICES)
            pitches = v_row[idx] * len(cfg.SCALE_DEGREES)
            pitches = np.clip(
                pitches.astype(int), 0, len(cfg.SCALE_DEGREES) - 1
            )
            freqs = cfg.BASE_FREQ * (2 ** (cfg.SCALE_DEGREES[pitches] / 12.0))
            amps = np.ones(cfg.MAX_VOICES) * v_mean * 2.0  # * 0.15

        # 3. Phase accumulation synthesis
        for v in range(cfg.MAX_VOICES):
            if freqs[v] > 0:
                phase_inc = freqs[v] * 2 * np.pi / cfg.SAMPLE_RATE
                self._phases[v] += phase_inc
                self._phases[v] %= 2 * np.pi
                outdata[:, 0] += amps[v] * np.sin(self._phases[v])
                outdata[:, 1] += amps[v] * np.sin(self._phases[v])

        # 4. Add noise floor (entropy-driven)
        noise_amp = (
            10
            ** (
                cfg.ENTROPY_NOISE_MIN
                + entropy * (cfg.ENTROPY_NOISE_MAX - cfg.ENTROPY_NOISE_MIN)
            )
            / 20
        )
        noise = np.random.randn(cfg.FRAMES_BLOCK_SIZE, 2) * noise_amp
        outdata += noise

        # 5. Simple 1-pole LPF (k controls cutoff)
        cutoff = cfg.K_FILTER_MIN + k * (cfg.K_FILTER_MAX - cfg.K_FILTER_MIN)
        alpha = 2 * np.pi * cutoff / cfg.SAMPLE_RATE
        alpha = np.clip(alpha, 0, 1)
        # Apply filter in-place (approximate)
        outdata[1:] = alpha * outdata[1:] + (1 - alpha) * outdata[:-1]

        # 6. Stereo panning
        left_gain = np.cos(0.5 * (pan + 1) * np.pi / 2)
        right_gain = np.sin(0.5 * (pan + 1) * np.pi / 2)
        outdata[:, 0] *= left_gain
        outdata[:, 1] *= right_gain

        # Clip to prevent distortion
        np.clip(outdata, -1.0, 1.0, out=outdata)
        """

    def start(self):
        self._stream = sd.OutputStream(
            samplerate=cfg.SAMPLE_RATE,
            blocksize=cfg.FRAMES_BLOCK_SIZE,
            channels=2,
            callback=self._callback,
        )
        self._stream.start()
        self._active = True

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
        self._active = False

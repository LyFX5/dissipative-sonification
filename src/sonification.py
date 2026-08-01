import numpy as np
import sounddevice as sd
import threading
import config as cfg


class AudioEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = {
            "f": cfg.DEFAULT_F,
            "k": cfg.DEFAULT_K,
            "v_mean": 0.0,
            "v_row": np.zeros(cfg.WIDTH),
            "entropy": 0.0,
            "gradient": 0.0,
            "pan": 0.0,
        }
        self._phases = np.zeros(cfg.MAX_VOICES)
        self._active = False
        self._stream = None
        self._buffer = np.zeros((cfg.FRAME_SIZE, 2))  # pre-allocate

    def update_state(self, new_state: dict):
        with self.lock:
            self.state.update(new_state)

    def _callback(self, outdata, frames, time, status):
        if status:
            print(f"⚠️ Audio callback status: {status}")
        with self.lock:
            f, k = self.state["f"], self.state["k"]
            v_row = self.state["v_row"]
            entropy = self.state["entropy"]
            gradient = self.state["gradient"]
            pan = self.state["pan"]

        # 1. Tempo/Event Rate → probability of triggering notes this frame
        bpm = cfg.F_TEMPO_MIN + (f * (cfg.F_TEMPO_MAX - cfg.F_TEMPO_MIN))
        event_prob = bpm / 60.0 / (cfg.SAMPLE_RATE / cfg.FRAME_SIZE)
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
            amps = np.ones(cfg.MAX_VOICES) * 0.15 * self.state["v_mean"]

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
        noise = np.random.randn(cfg.FRAME_SIZE, 2) * noise_amp
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

    def start(self):
        self._stream = sd.OutputStream(
            samplerate=cfg.SAMPLE_RATE,
            blocksize=cfg.FRAME_SIZE,
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

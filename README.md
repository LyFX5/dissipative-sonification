# README.md

# 🔬 Dissipative Sonification

> **Interactive simulation & audio mapping of far-from-equilibrium pattern emergence**
> 

[Python](https://img.shields.io/badge/Python-3.9+-blue)

[License](https://img.shields.io/badge/License-MIT-green)

[Dependencies](https://img.shields.io/badge/Dependencies-4-orange)

---

## 🌌 Ideology

This project bridges **non-equilibrium thermodynamics**, **complex systems theory**, and **algorithmic sonification**. Dissipative structures (Prigogine, 1977) are macroscopic patterns that emerge only when a system is pushed far from equilibrium, sustained by continuous energy input and entropy export.

Traditional visualizations show *what* emerges, but often miss *how* it feels to exist near bifurcation thresholds. By mapping simulation state variables directly to perceptual audio dimensions, this tool creates an **embodied cognitive channel**: you hear phase transitions, feel entropy export, and intuitively grasp nonlinear feedback through rhythm, timbre, and spatial movement.

**Core Principle**: *Sound is time. Emergence is temporal. Mapping one to the other reveals dynamics that static images hide.*

---

## 🏗️ Architecture

```
                 ┌──────────────────────┐
                 │      Qt Event Loop   │
                 │  (QTimer @ ~24 Hz)   │
                 │                      │
  Mouse scrub ──▶│  MatrixWidget        │──▶ add_brush()
                 │    (QPainter)        │
                 └──────────┬───────────┘
                            │ GrayScott.step()
                            ▼
                 ┌──────────────────────┐
                 │  Simulation Core     │
                 │   (Gray-Scott PDE)   │
                 └──────────┬───────────┘
                            │ get_metrics()
                            ▼
              ┌─────────────┴─────────────┐
              │     Thread-Safe State     │
              │         (lock)            │
              └─────────────┬─────────────┘
                            │ update_state()
              ┌─────────────┴─────────────┐
              │   AudioEngine (PortAudio  │  ◀─ separate callback thread
              │   real-time synth)        │
              └───────────────────────────┘
```

### 🔄 Data Flow

1. **Pipeline Tick**: A single `QTimer` fires ~24×/sec (Qt thread): simulate a step → merge any brushed concentration → extract metrics → push to the audio engine → repaint matrix → update plots.
2. **Metrics Extraction**: `get_metrics()` computes entropy, gradient, spatial centroid, and the V-field row.
3. **State Buffer**: Thread-safe dict (lock) updated each tick; read by the audio callback.
4. **Audio Callback**: `sounddevice` runs on its own thread at 44.1 kHz, reads the latest state, and synthesizes each frame of audio.
5. **Sonification Mapping**:
    - `f` (feed) → Event probability / rhythmic density
    - `k` (kill) → Low-pass filter cutoff / timbral brightness
    - `V` row → Pitch quantization (Dorian scale)
    - `Entropy` → Noise floor amplitude
    - `Centroid` → Stereo panning
    - `Gradient` → Harmonic saturation index

---

## 📁 Structure

dissipative-sonification/
├── README.md                 # Project documentation (this file)
├── requirements.txt          # Python dependencies
└── src/
    ├── init.py               # Package marker
    ├── config.py             # Constants, scales, mapping ranges, brush params
    ├── simulation.py         # Gray-Scott solver, feature extraction, brush injection
    ├── sonification.py       # Real-time audio synthesis engine (PortAudio thread)
    ├── qt_app.py             # Main window: splitter layout + QTimer pipeline
    ├── matrix_widget.py      # Interactive QPainter matrix (mouse-scrub painting)
    ├── plots_widget.py       # Animated energy / entropy / concentration / phase-plane
    ├── controls_widget.py    # Sliders & value boxes for f, k; pause/reset
    └── main.py               # Entry point, QApplication, thread coordination

> The GUI is built with **PySide6 (Qt)**. A single `QTimer` drives the
> simulation + rendering + metric push each tick, while `sounddevice` runs
> audio on its own PortAudio callback thread. There is no separate pygame or
> matplotlib event loop — everything shares the one Qt event loop.

---

## 🛠️ Technical Support

### Installation

```bash
git clone <repo-url>
cd dissipative-sonification
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

**Note**: `sounddevice` requires PortAudio. It installs automatically on most platforms via wheels. If it fails, install PortAudio via your OS package manager (`brew install portaudio` / `sudo apt install portaudio19-dev`).

**Running**

```bash
python -m dissipative_sonification.main
```

### Controls

- **Matrix (left)**: Click or scrube with the cursor to inject concentration (V) — and deplete U — along the trajectory, feeding the live simulation.
- **Feed (f)**: Controls energy input. Higher `f` → faster rhythms, more events
- **Kill (k)**: Controls dissipation. Higher `k` → brighter timbre, faster decay
- **Pause/Resume**: Halts simulation & audio scheduling
- **Reset**: Re-seeds the field and clears painted concentration
- **Window Close**: Safely shuts down audio stream and exits

### Troubleshooting

| Issue | Solution |
| --- | --- |
| `OSError: PortAudio not found` | Install PortAudio system package or use `conda install portaudio` |
| `Audio crackling/drops` | Increase `FRAME_SIZE` in `config.py` to 2048 or 4096 |
| Qt window fails to open | Ensure PySide6 is installed: `pip install PySide6` |
| `No sound` | Check system audio output device; ensure stream is active in OS mixer |

### Extending

- **Add new metrics**: Modify `simulation.get_metrics()` and map in `sonification.py`
- **Change scale**: Edit `SCALE_DEGREES` in `config.py` (use MIDI intervals)
- **Export audio**: Use `soundfile` to record `outdata` in the callback
- **GPU acceleration**: Replace numpy solver with `cupy` or `taichi` for >512x512 grids

## 📜 License

MIT License. Free to use, modify, and distribute. Third-party libraries governed by their respective licenses.

> 💡 *Treat this as a laboratory for perceptual systems theory. The code is a scaffold; the phenomena are yours to explore.*
> 

---

### 🚀 How to Run & Validate

1. Install dependencies (`pip install -r requirements.txt`, in your conda env)
2. Run `python -m dissipative_sonification.main`
3. Paint on the matrix and adjust sliders:
    - `f ≈ 0.055, k ≈ 0.062` → spots & mitosis → rhythmic, pitched textures
    - `f > 0.08, k < 0.05` → traveling waves → arpeggiated, panning sequences
    - `f < 0.04` → homogeneous decay → ambient drone + rising noise
4. Close window to safely terminate audio thread

The architecture is deliberately minimal to prioritize **understanding over abstraction**. Every mapping is explicit, every parameter is tunable, and the codebase is structured to let you experiment, log, and extend without fighting framework overhead.

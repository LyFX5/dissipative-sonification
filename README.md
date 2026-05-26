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

┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   UI Controls   │────▶│  Simulation Core │────▶│  State Sampler  │
│ (f, k sliders)  │     │  (Gray-Scott PDE)│     │  (Metrics Calc) │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
│
┌─────────────────┐     ┌──────────────────┐     ┌────────▼────────┐
│   Matplotlib    │◀────│  Animation Loop  │◀────│  Thread-Safe    │
│   Visualization │     │  (50ms refresh)  │     │  State Buffer   │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
│
┌─────────────────┐     ┌──────────────────┐     ┌────────▼────────┐
│   Audio Output  │◀────│  Real-Time Synth │◀────│  Callback Engine│
│   (PortAudio)   │     │  (Phase Acc + LPF)│     │  (sounddevice)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘

### 🔄 Data Flow

1. **Simulation**: Vectorized Gray-Scott solver runs on main thread via `matplotlib.animation.FuncAnimation`
2. **Metrics Extraction**: `get_metrics()` computes entropy, gradient, spatial centroid, and V-field row
3. **State Buffer**: Thread-safe dictionary updated at ~20Hz
4. **Audio Callback**: `sounddevice` runs at 44.1kHz, reads latest state, generates frame of audio
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
    ├── init.py           # Package marker
    ├── config.py             # Constants, scales, mapping ranges
    ├── simulation.py         # Gray-Scott solver & feature extraction
    ├── sonification.py       # Real-time audio synthesis engine
    ├── viz.py                # Matplotlib UI, sliders, animation loop
    └── main.py               # Entry point, thread coordination

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
python -m src.main
```

### Controls

- **Feed (f)**: Controls energy input. Higher `f` → faster rhythms, more events
- **Kill (k)**: Controls dissipation. Higher `k` → brighter timbre, faster decay
- **Pause/Resume**: Halts simulation & audio scheduling
- **Window Close**: Safely shuts down audio stream and exits

### Troubleshooting

| Issue | Solution |
| --- | --- |
| `OSError: PortAudio not found` | Install PortAudio system package or use `conda install portaudio` |
| `Audio crackling/drops` | Increase `FRAME_SIZE` in `config.py` to 2048 or 4096 |
| `Matplotlib GUI freezes` | Run with `MPLBACKEND=Qt5Agg` or `TkAgg` |
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

1. Install dependencies
2. Run `python -m src.main`
3. Adjust sliders:
    - `f ≈ 0.055, k ≈ 0.062` → spots & mitosis → rhythmic, pitched textures
    - `f > 0.08, k < 0.05` → traveling waves → arpeggiated, panning sequences
    - `f < 0.04` → homogeneous decay → ambient drone + rising noise
4. Close window to safely terminate audio thread

The architecture is deliberately minimal to prioritize **understanding over abstraction**. Every mapping is explicit, every parameter is tunable, and the codebase is structured to let you experiment, log, and extend without fighting framework overhead.

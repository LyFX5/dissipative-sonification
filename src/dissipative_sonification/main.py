#!/usr/bin/env python3
"""
Dissipative Sonification: Interactive Simulation & Audio Mapping
Entry point for running the Gray-Scott reaction-diffusion sonification studio.
"""

import sys
from PySide6.QtWidgets import QApplication

from dissipative_sonification.simulation import GrayScott
from dissipative_sonification.sonification import AudioEngine
from dissipative_sonification.qt_app import QApp


def main():
    print("🔬 Initializing Dissipative Sonification Studio...")
    print("🎨 Paint on the matrix, scrub to inject concentration.")
    print("🎛️  Adjust Feed (f) and Kill (k) on the right.")
    print("🔊 Audio maps: f→tempo, k→filter, V→pitch, entropy→noise, centroid→pan")
    print("⚠️  Close window or press Ctrl+C to stop.")

    app = QApplication.instance() or QApplication(sys.argv)
    sim = GrayScott()
    audio = AudioEngine()
    window = QApp(sim, audio)
    window.show()
    window.start()

    try:
        exit_code = app.exec()
    except KeyboardInterrupt:
        exit_code = 0
    finally:
        window.shutdown()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

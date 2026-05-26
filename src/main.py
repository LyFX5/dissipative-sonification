#!/usr/bin/env python3
"""
Dissipative Sonification: Interactive Simulation & Audio Mapping
Entry point for running the Gray-Scott reaction-diffusion sonification.
"""
import sys
from .simulation import GrayScott
from .sonification import AudioEngine
from .viz import Visualizer

def main():
    print("🔬 Initializing Dissipative Sonification Pipeline...")
    print("🎛️  Use sliders to adjust Feed (f) and Kill (k) parameters.")
    print("🔊 Audio maps: f→tempo, k→filter, V→pitch, entropy→noise, centroid→pan")
    print("⚠️  Close window or press Ctrl+C to stop.")

    sim = GrayScott()
    audio = AudioEngine()
    viz = Visualizer(sim, audio)
    
    try:
        viz.run()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        audio.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()

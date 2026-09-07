import sys
import numpy as np
import sounddevice as sd
# sd._initialize(portaudio_host_api_type=1)

device = 1  # Uses default (ALC257 Analog)
amplitude = 1.0
frequency = 440.0
start_idx = 0

samplerate = 4000

try:
    # samplerate = sd.query_devices(device, 'output')['default_samplerate']

    def callback(outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        global start_idx
        t = (start_idx + np.arange(frames)) / samplerate
        t = t.reshape(-1, 1)
        outdata[:] = amplitude * np.sin(2 * np.pi * frequency * t)
        start_idx += frames

    with sd.OutputStream(device=device, channels=1, callback=callback,
                         samplerate=samplerate):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()

except Exception as e:
    print(f"Error: {e}")


'''
def callback(outdata, frames, time, status):
    outdata[:] = np.random.uniform(-0.5, 0.5, outdata.shape)  # White noise

with sd.OutputStream(device=1, channels=2, callback=callback):
    print("Playing white noise on device 1 (ALC257). Press Enter to stop.")
    input()
'''

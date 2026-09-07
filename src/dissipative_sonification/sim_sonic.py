import time

from dissipative_sonification.simulation import GrayScott
from dissipative_sonification.sonification import AudioEngine


def main():

    steps = 5

    sim = GrayScott()
    audio = AudioEngine()

    audio.start()

    for i in range(steps):

        metrics = sim.get_metrics()
        audio.update_state(metrics)
        time.sleep(1)

        ctr = input()

        if ctr == "end":
            break
        else:
            ctr = float(ctr)

        sim.f = ctr / 10000

        sim.step()

    audio.stop()

    # its remain to build and integrate here a visualiser
    # I think that matplot lib blocs the thread and will not work here


if __name__ == "__main__":
    main()

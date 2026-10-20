from dissipative_sonification.simulation import GrayScott
from dissipative_sonification.matplotlib_animation import Visualizer


def main():

    sim = GrayScott()

    vis = Visualizer(sim)

    vis.run()


if __name__ == "__main__":
    main()

import argparse
from os import listdir, path

import matplotlib.pyplot as plt
import numpy as np

from util import get_distances

parser = argparse.ArgumentParser(
    description='Visualize interface lines of physical deposition models with different sticking probabilities.')
parser.add_argument('DIR',
                    type=str,
                    help='results directory')


def main():
    # Parse the command line arguments
    args = parser.parse_args()

    tx, ty, distances = get_distances(args.DIR)

    sidewall_idx = np.where(np.bitwise_and(
        np.bitwise_and(tx < 0, ty < -0.5), ty > np.min(ty)+0.5))

    for sticking_probability, distance in distances.items():
        plt.plot(-ty[sidewall_idx], distance[sidewall_idx],
                 label="$s=2^{-"+str(sticking_probability)+"}$")
    plt.xlabel("Trench depth [nm]")
    #plt.xlabel("element index along trench substrate interface line")
    plt.ylabel("Deposition thickness [nm]")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()

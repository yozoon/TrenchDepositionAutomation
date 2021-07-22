import argparse
from os import listdir, path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(
    description='Visualize interface lines of physical deposition models with different sticking probabilities.')
parser.add_argument('csv',
                    type=str,
                    help='CSV input file')


def main():
    # Parse the command line arguments
    args = parser.parse_args()
    df = pd.read_csv(args.csv, index_col=0)

    # Extract the geometry rows
    tx = df.iloc[0].to_numpy()
    ty = df.iloc[1].to_numpy()

    # Remove the geometry rows
    df = df.iloc[2:]

    # Mask off all elements except those contributing to the left sidewall
    sidewall_mask = (tx < 0) & (ty < -0.5) & (ty > np.min(ty) + 0.5)

    # Plot the results
    for s, dist in df.iterrows():
        plt.plot(-ty[sidewall_mask], dist[sidewall_mask],
                 label=f"s={s}")  # "$s=2^{-"+str(s)+"}$")
    plt.xlabel("y position [nm]")
    plt.ylabel("Deposition thickness [nm]")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()

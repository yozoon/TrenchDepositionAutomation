import argparse
from os import listdir, path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(
    description='Visualize interface lines of physical deposition models with different sticking probabilities.')
parser.add_argument('input',
                    type=str,
                    help='CSV input file')


def main():
    # Parse the command line arguments
    args = parser.parse_args()
    # Enforce csv file ending and generate additional filename for csv file for saving the geometry
    basename = path.splitext(args.input)[0]
    data_fname = basename + ".csv"
    geometry_fname = basename + "_geom.csv"

    data_df = pd.read_csv(data_fname, header=None)
    data_df.columns = ["geometry_id",
                       "sticking_probability"] + data_df.columns[:-2].to_list()
    geom_df = pd.read_csv(geometry_fname, header=None)
    geom_df.columns = ["geometry_id", "axis"] + geom_df.columns[:-2].to_list()

    for geometry_id in geom_df["geometry_id"].unique():
        tx = geom_df[(geom_df["geometry_id"] == geometry_id) & (
            geom_df["axis"] == 0)].drop(["geometry_id", "axis"], axis=1).to_numpy()[0]
        ty = geom_df[(geom_df["geometry_id"] == geometry_id) & (
            geom_df["axis"] == 1)].drop(["geometry_id", "axis"], axis=1).to_numpy()[0]

        df = data_df[data_df["geometry_id"] == geometry_id].drop(
            ["geometry_id"], axis=1).groupby("sticking_probability").mean()

        print(df)
        print(tx, ty)

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

    """
    fig, ax = plt.subplots(figsize=(9,16))
    ax.plot(tx, ty)

    for mx, my, r in zip(tx, ty, df.iloc[0]):
        ax.add_patch(plt.Circle((mx, my), r, color='b', fill=False, clip_on=True))
    # Label plot
    ax.set_xlabel("x [nm]")
    ax.set_ylabel("y [nm]")
    ax.legend(loc="upper center")
    plt.axis("scaled")
    plt.show()
    """


if __name__ == "__main__":
    main()

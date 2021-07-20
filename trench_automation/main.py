from argparse import ArgumentParser
from subprocess import Popen
from os import path
from string import Template
from tempfile import NamedTemporaryFile

import numpy as np
import pandas as pd

import util

# This only works if the directory where "generate_trench.so" is located is present in the PYTHONPATH environment variable
#import generate_trench


VIENNATS_EXE = "../../ViennaTools/ViennaTS/build/viennats-2.3.2"
PROJECT_DIRECTORY = path.dirname(__file__)
PROCESS_TIME = 10
DISTANCE_BITS = 8
OUTPUT_DIR = path.join(PROJECT_DIRECTORY, "output")
N = 12


parser = ArgumentParser(
    description='Run physical deposition simulations with different sticking probabilities.')
parser.add_argument('CSV',
                    type=str,
                    default="results.csv",
                    nargs="?",
                    help='CSV file for saving the results')


def main():
    args = parser.parse_args()

    # Read the template file into a string variable
    with open(path.join(PROJECT_DIRECTORY, "parameters.template"), "r") as f:
        template_string = f.read()

    tx, ty = None, None

    deposition_thickness = []

    for i in range(N+1):
        sticking_probability = 1/2**i
        print(f"Sticking probability: {sticking_probability}")
        # Use the template to create the content of the parameter file
        s = Template(template_string)
        out = s.substitute(
            GEOMETRY_FILE=path.join(PROJECT_DIRECTORY, "trench.vtk"),
            DISTANCE_BITS=DISTANCE_BITS,
            OUTPUT_PATH=OUTPUT_DIR,  # path.join(OUTPUT_DIR, f"result_{i}"),
            FD_SCHEME="LAX_FRIEDRICHS_1ST_ORDER",
            PROCESS_TIME=PROCESS_TIME,
            # ",".join([str(i) for i in range(11)]),
            OUTPUT_VOLUME=PROCESS_TIME,
            DEPOSITION_RATE="1.",
            STICKING_PROBABILITY=sticking_probability,
            STATISTICAL_ACCURACY="1000.")

        # Create a temporary file with the content we just generated
        # which can be used as an input for ViennaTS
        paramfile = NamedTemporaryFile(mode='w+')
        paramfile.file.write(out)
        paramfile.file.flush()

        # Call ViennaTS with the just generated temporary process definition file
        Popen([VIENNATS_EXE, paramfile.name],
              cwd=PROJECT_DIRECTORY).wait()

        # Close/ Destroy the tempfile
        paramfile.close()

        # Load the points along the trench surface, if they aren't already loaded
        if tx is None:
            tx, ty, _ = util.extract_line(
                path.join(OUTPUT_DIR + f"_{DISTANCE_BITS}bit", "Interface_0_0.vtp"))

        # Load the points along the surface of the deposited layer
        x, y, _ = util.extract_line(
            path.join(OUTPUT_DIR + f"_{DISTANCE_BITS}bit", "Interface_1_0.vtp"))

        # Calculate the layer thickness
        dist = util.line_to_distance(tx, ty, x, y)
        # Add the layer thickness to the array, but first append the current sticking probability to them
        deposition_thickness.append(np.insert(dist, 0, sticking_probability))

    # Add the x and y coordinates of the trench geometry to the array
    deposition_thickness.insert(0, np.insert(ty, 0, -1))
    deposition_thickness.insert(0, np.insert(tx, 0, -1))

    # Convert the results into a pandas DataFrame
    df = pd.DataFrame(deposition_thickness)
    # Set the sticking probability as the index
    df.index = df[0]
    df.index.rename("sticking_probability", inplace=True)
    df.drop(0, inplace=True, axis=1)

    # Print the DataFrame
    print(df)

    # Save the DataFrame as a csv file
    df.to_csv(args.CSV, index=True, header=True)

    print("Done!")


if __name__ == "__main__":
    main()

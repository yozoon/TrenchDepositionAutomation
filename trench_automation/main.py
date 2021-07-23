import csv
from argparse import ArgumentParser, ArgumentTypeError
from os import path
from string import Template
from subprocess import Popen
from tempfile import NamedTemporaryFile

import numpy as np

import util

# This import only works if the directory where "generate_trench.so" is located is present in
# the PYTHONPATH environment variable
#import generate_trench


VIENNATS_EXE = "../../ViennaTools/ViennaTS/build/viennats-2.3.2"
PROJECT_DIRECTORY = path.dirname(__file__)
PROCESS_TIME = 10
DISTANCE_BITS = 8
OUTPUT_DIR = path.join(PROJECT_DIRECTORY, "output")

parser = ArgumentParser(
    description="Run physical deposition simulations with different sticking probabilities.")
parser.add_argument(
    "output",
    type=str,
    default="results.csv",
    nargs="?",
    help="output CSV file for saving the results")


def check_list_input(x):
    """ Converts the input string to a list of floats. Only uses input elements with a value between 0 and 1."""
    x = x.replace("[", "").replace("]", "").split(",")
    try:
        x = [float(i) for i in x]
    except ValueError as e:
        raise ArgumentTypeError(e)

    if np.all([0 < i <= 1 for i in x]):
        if len(x) == 0:
            raise ArgumentTypeError("No sticking probability values provided")
        return x
    else:
        raise ArgumentTypeError(
            "The sticking probability has to have a value between 0 and 1.")


parser.add_argument(
    "--sticking-probabilities",
    dest="sticking_probabilities",
    type=check_list_input,
    default=[1/2**i for i in range(5)],
    help="list of sticking probabilities to be used during the simulation"
)

parser.add_argument(
    "--repetitions",
    dest="repetitions",
    type=int,
    default=10,
    help="how often the simulation should be repeated for one set of parameters")


def main():
    args = parser.parse_args()
    # Read the template file into a string variable
    with open(path.join(PROJECT_DIRECTORY, "parameters.template"), "r") as f:
        template_string = f.read()

    # Enforce csv file ending and generate additional filename for csv file for saving the geometry
    basename = path.splitext(args.output)[0]
    data_fname = basename + ".csv"
    geometry_fname = basename + "_geom.csv"

    # Open the files and create csv writers for them
    with open(data_fname, "w+") as datafile, open(geometry_fname, "w+") as geomfile:
        data_writer = csv.writer(datafile)
        geometry_writer = csv.writer(geomfile)

        # Here we could generate new trench geometries using the generate_trench module...

        tx, ty = None, None
        geometry_id = -1

        for sticking_probability in args.sticking_probabilities:
            print(f"Sticking probability: {sticking_probability}")
            # Use the template to create the content of the parameter file
            s = Template(template_string)
            out = s.substitute(
                GEOMETRY_FILE=path.join(PROJECT_DIRECTORY, "trench.vtk"),
                DISTANCE_BITS=DISTANCE_BITS,
                # path.join(OUTPUT_DIR, f"result_{i}"),
                OUTPUT_PATH=OUTPUT_DIR,
                FD_SCHEME="LAX_FRIEDRICHS_1ST_ORDER",
                PROCESS_TIME=PROCESS_TIME,
                # ",".join([str(i) for i in range(11)]),
                OUTPUT_VOLUME=PROCESS_TIME,
                DEPOSITION_RATE="1.",
                STICKING_PROBABILITY=sticking_probability,
                STATISTICAL_ACCURACY="1000.")

            # Create a temporary file with the content we just generated
            # which can be used as an input for ViennaTS
            with NamedTemporaryFile(mode="w+") as paramfile:
                paramfile.file.write(out)
                paramfile.file.flush()

                for _ in range(args.repetitions):
                    # Call ViennaTS with the just generated temporary process definition file
                    Popen([VIENNATS_EXE, paramfile.name],
                          cwd=PROJECT_DIRECTORY).wait()

                    # Load the points along the trench surface, if they aren't already loaded
                    if tx is None:
                        tx, ty, _ = util.extract_line(
                            path.join(OUTPUT_DIR + f"_{DISTANCE_BITS}bit", "Interface_0_0.vtp"))
                        geometry_id = geometry_id + 1
                        geometry_writer.writerow(
                            [geometry_id, 0] + tx.flatten().tolist())
                        geometry_writer.writerow(
                            [geometry_id, 1] + ty.flatten().tolist())

                    # Load the points along the surface of the deposited layer
                    x, y, _ = util.extract_line(
                        path.join(OUTPUT_DIR + f"_{DISTANCE_BITS}bit", "Interface_1_0.vtp"))

                    # Calculate the layer thickness
                    dist = util.line_to_distance(tx, ty, x, y)

                    # Add the layer thickness to the array, but first append the current geometry_id and
                    # sticking probability to them
                    data_writer.writerow([geometry_id, sticking_probability] +
                                         dist.flatten().tolist())

    print("Done!")


if __name__ == "__main__":
    main()

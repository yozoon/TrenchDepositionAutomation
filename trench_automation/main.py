import subprocess
from os import path
from string import Template
from tempfile import NamedTemporaryFile

import numpy as np

VIENNATS_EXE = "../../ViennaTools/ViennaTS/build/viennats-2.3.2"
PROJECT_DIRECTORY = path.dirname(__file__)

# Read the template file into a string variable
with open(path.join(PROJECT_DIRECTORY, "parameters.template"), "r") as f:
    template_string = f.read()

PROCESS_TIME=10
OUTPUT_DIR= path.join(PROJECT_DIRECTORY, "output")

N = 10

for i in range(12): #np.linspace(1/N, 1, N, endpoint=True):
    sticking_probability = 1/2**i
    print(f"Sticking probability: {sticking_probability}")
    # Use the template to create the content of the parameter file
    s = Template(template_string)
    out = s.substitute(
        GEOMETRY_FILE=path.join(PROJECT_DIRECTORY, "trench.vtk"),
        OUTPUT_PATH=path.join(OUTPUT_DIR, f"result_{i}"),
        FD_SCHEME="LAX_FRIEDRICHS_1ST_ORDER",
        PROCESS_TIME=PROCESS_TIME,
        OUTPUT_VOLUME=PROCESS_TIME, #",".join([str(i) for i in range(11)]),
        DEPOSITION_RATE="1.",
        STICKING_PROBABILITY=sticking_probability,
        STATISTICAL_ACCURACY="1000.")

    # Create a temporary file with the content we just generated
    # which can be used as an input for ViennaTS
    paramfile = NamedTemporaryFile(mode='w+')
    paramfile.file.write(out)
    paramfile.file.flush()

    # Call ViennaTS with the process parameter file
    subprocess.Popen([VIENNATS_EXE, paramfile.name], cwd=PROJECT_DIRECTORY).wait()
    
    # Close/ Destroy the tempfile
    paramfile.close()

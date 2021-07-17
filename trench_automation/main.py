import subprocess
from os import path
from string import Template
from tempfile import NamedTemporaryFile

VIENNATS_EXE = "../../ViennaTools/ViennaTS/build/viennats-2.3.2"
PROJECT_DIRECTORY = path.dirname(__file__)

# Read the template file into a string variable
with open(path.join(PROJECT_DIRECTORY, "parameters.template"), "r") as f:
    template_string = f.read()

# Use the template to create the parameter file
s = Template(template_string)
out = s.substitute(
    GEOMETRY_FILE=path.join(PROJECT_DIRECTORY, "trench.vtk"),
    OUTPUT_PATH=path.join(PROJECT_DIRECTORY, "results"),
    FD_SCHEME="LAX_FRIEDRICHS_1ST_ORDER",
    DEPOSITION_RATE="1.",
    STICKING_PROBABILITY="1.",
    STATISTICAL_ACCURACY="1000.")

# Create a temporary file containing the process definitions
# which can be used as an input for ViennaTS
paramfile = NamedTemporaryFile(mode='w+')
paramfile.file.write(out)
paramfile.file.flush()

# Call ViennaTS with the process parameter file
subprocess.Popen([VIENNATS_EXE, paramfile.name], cwd=PROJECT_DIRECTORY).wait()

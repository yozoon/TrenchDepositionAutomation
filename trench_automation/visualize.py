import argparse
from os import listdir, path

import matplotlib.pyplot as plt
import numpy as np
import sklearn.neighbors as neighbors
import vtk
from vtk.util.numpy_support import vtk_to_numpy

parser = argparse.ArgumentParser(
    description='Visualize interface lines of physical deposition models with different sticking probabilities.')
parser.add_argument('DIR',
                    type=str,
                    help='results directory')


def extract_line(filename):
    # Read the VTP file
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()

    # Extract the polygon data
    polydata = reader.GetOutput()

    # Apply a filter to connect contiguous line segments
    # (This step is necessary since otherwise we would have many small line elements)
    strip = vtk.vtkStripper()
    strip.SetInputData(polydata)
    strip.SetJoinContiguousSegments(True)
    strip.Update()

    # Retrieve the filter output
    filtered = strip.GetOutput()

    # Extract Points
    point_coordinates = vtk_to_numpy(filtered.GetPoints().GetData())

    # Extract Line data
    lines = filtered.GetLines()
    lines_array = vtk_to_numpy(lines.GetData())

    # Extract the surface line (as separate x, y and z array)
    return [np.array(d) for d in point_coordinates[lines_array[1:]].T]


def main():
    # Parse the command line arguments
    args = parser.parse_args()
    tx = None
    ty = None
    distances = {}
    for subdir in listdir(args.DIR):
        i = int(subdir.split("_")[1])
        #sticking_probability = float(subdir.split("_")[1])
        #print(sticking_probability)
        # Only extract the trench geometry once
        if tx is None:
            tx, ty, _ = extract_line(
                path.join(args.DIR, subdir, "Interface_0_0.vtp"))

        x, y, _ = extract_line(
            path.join(args.DIR, subdir, "Interface_1_0.vtp"))

        nbrs = neighbors.NearestNeighbors(
            n_neighbors=1, metric="euclidean").fit(np.vstack([x, y]).T)
        dist, _ = nbrs.kneighbors(np.vstack([tx, ty]).T)

        distances[i] = dist

    sidewall_idx = np.where(np.bitwise_and(
        np.bitwise_and(tx < 0, ty < -0.5), ty > np.min(ty)+0.5))

    for sticking_probability, distance in distances.items():
        plt.plot(-ty[sidewall_idx], distance[sidewall_idx],
                 label=f"s={sticking_probability}")
    plt.xlabel("Trench depth [nm]")
    #plt.xlabel("element index along trench substrate interface line")
    plt.ylabel("Deposition thickness [nm]")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()

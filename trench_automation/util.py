from os import path, listdir

import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

import sklearn.neighbors as neighbors

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


def line_to_distance(tx, ty, x, y):
    nbrs = neighbors.NearestNeighbors(
        n_neighbors=1, metric="euclidean").fit(np.vstack([x, y]).T)
    dist, _ = nbrs.kneighbors(np.vstack([tx, ty]).T)
    return dist


def get_distances(directory):
    tx = None
    ty = None
    distances = {}
    for subdir in listdir(directory):
        i = int(subdir.split("_")[1])
        #sticking_probability = float(subdir.split("_")[1])
        # print(sticking_probability)
        # Only extract the trench geometry once
        if tx is None:
            tx, ty, _ = extract_line(
                path.join(directory, subdir, "Interface_0_0.vtp"))

        x, y, _ = extract_line(
            path.join(directory, subdir, "Interface_1_0.vtp"))

        distances[i] = line_to_distance(tx, ty, x, y)

    return tx, ty, distances

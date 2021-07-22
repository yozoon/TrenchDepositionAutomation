from os import listdir, path

import numpy as np
import sklearn.neighbors as neighbors
import vtk
from vtk.util.numpy_support import vtk_to_numpy


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

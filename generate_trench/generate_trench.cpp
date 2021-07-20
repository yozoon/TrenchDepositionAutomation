#include <iostream>
#include <pybind11/pybind11.h>

#include <lsBooleanOperation.hpp>
#include <lsExpand.hpp>
#include <lsGeometricAdvect.hpp>
#include <lsMakeGeometry.hpp>
#include <lsToDiskMesh.hpp>
#include <lsToMesh.hpp>
#include <lsToSurfaceMesh.hpp>
#include <lsVTKWriter.hpp>
#include <lsWriteVisualizationMesh.hpp>

namespace py = pybind11;

class Trench {
private:
  typedef double NumericType;
  static constexpr int D = 2;

  double gridDelta;
  double extent;

  lsSmartPointer<lsDomain<NumericType, D>> substrate;

  hrleVectorType<double, 2> center;
  hrleVectorType<double, 2> taperAngle;
  double diameter;
  double depth;

public:
  Trench()
      : gridDelta(1.), extent(20.), center(0., 0.), taperAngle(1., 0.),
        diameter(20.), depth(50.) {}

  void setGridDelta(double delta) { this->gridDelta = delta; }

  void setExtent(double ext) { this->extent = ext; }

  void setDiameter(double diam) { this->diameter = diam; }

  void setDepth(double d) { this->depth = d; }

  void setCenter(double centerX, double centerY) {
    this->center[0] = centerX;
    this->center[1] = centerY;
  }

  void setTaperAngle(double nx, double ny) {
    this->taperAngle[0] = nx;
    this->taperAngle[1] = ny;
  }

  void generate() {
    double bounds[2 * D] = {-extent, extent, -3 * extent, 3 * extent};
    if constexpr (D == 3) {
      bounds[4] = -extent;
      bounds[5] = extent;
    }

    typename lsDomain<NumericType, D>::BoundaryType boundaryCons[D];
    for (unsigned i = 0; i < D - 1; ++i) {
      boundaryCons[i] =
          lsDomain<NumericType, D>::BoundaryType::REFLECTIVE_BOUNDARY;
    }
    boundaryCons[D - 1] =
        lsDomain<NumericType, D>::BoundaryType::INFINITE_BOUNDARY;

    substrate = lsSmartPointer<lsDomain<NumericType, D>>::New(
        bounds, boundaryCons, gridDelta);
    {
      NumericType origin[D] = {0., 0.};
      NumericType planeNormal[D] = {0., 1.};
      auto plane =
          lsSmartPointer<lsPlane<NumericType, D>>::New(origin, planeNormal);
      lsMakeGeometry<NumericType, D>(substrate, plane).apply();
    }

    // make LS from trench mesh and remove from substrate
    auto trench = lsSmartPointer<lsDomain<NumericType, D>>::New(
        bounds, boundaryCons, gridDelta);
    {
      // create trench
      auto trenchMesh = lsSmartPointer<lsMesh<>>::New();

      auto cloud = lsSmartPointer<lsPointCloud<double, 2>>::New();
      {
        // top left
        hrleVectorType<double, 2> point1(-diameter / 2., 0.);
        cloud->insertNextPoint(point1);
        // top right
        hrleVectorType<double, 2> point2(diameter / 2., 0.);
        cloud->insertNextPoint(point2);
        // bottom right
        hrleVectorType<double, 2> point3(
            diameter / 2. - (depth * taperAngle[1] / taperAngle[0]), -depth);
        cloud->insertNextPoint(point3);
        // bottom left
        hrleVectorType<double, 2> point4(
            -diameter / 2. + (depth * taperAngle[1] / taperAngle[0]), -depth);
        cloud->insertNextPoint(point4);
      }
      lsConvexHull<double, 2>(trenchMesh, cloud).apply();

      lsFromSurfaceMesh<double, D>(trench, trenchMesh, false).apply();
      lsBooleanOperation<double, D>(substrate, trench,
                                    lsBooleanOperationEnum::RELATIVE_COMPLEMENT)
          .apply();
    }
  }

  void save(std::string filename = "trench.vtk") {
    std::cout << "Saving Geometry" << std::endl;
    auto mesh = lsSmartPointer<lsMesh<>>::New();
    lsToSurfaceMesh<NumericType, D>(substrate, mesh).apply();
    lsVTKWriter(mesh, filename).apply();
  }
};

PYBIND11_MODULE(generate_trench, m) {
  py::class_<Trench>(m, "Trench")
      .def(py::init<>())
      .def("setGridDelta", &Trench::setGridDelta)
      .def("setExtent", &Trench::setExtent)
      .def("setDiameter", &Trench::setDiameter)
      .def("setDepth", &Trench::setDepth)
      .def("setCenter", &Trench::setCenter)
      .def("generate", &Trench::generate)
      .def("save", &Trench::save);
}
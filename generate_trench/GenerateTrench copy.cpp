#include <boost/program_options.hpp>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <lsBooleanOperation.hpp>
#include <lsExpand.hpp>
#include <lsGeometricAdvect.hpp>
#include <lsMakeGeometry.hpp>
#include <lsToDiskMesh.hpp>
#include <lsToMesh.hpp>
#include <lsToSurfaceMesh.hpp>
#include <lsVTKWriter.hpp>
#include <lsWriteVisualizationMesh.hpp>

namespace po = boost::program_options;

void makeTaperedTrench(lsSmartPointer<lsMesh<>> mesh,
                       hrleVectorType<double, 2> center,
                       hrleVectorType<double, 2> taperAngle, double diameter,
                       double depth) {
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
  lsConvexHull<double, 2>(mesh, cloud).apply();
}

std::array<double, 2> strToArray(const std::string &str) {
  std::stringstream ss(str);
  std::string tmp;
  std::array<double, 2> data;
  int i = 0;
  while (std::getline(ss, tmp, ',')) {
    std::stringstream conv(tmp);
    double value;
    if (!(conv >> value)) {
      std::cout << "Error converting element " << i << " of input " << str
                << std::endl;
      exit(-1);
    }
    data[i] = value;
    ++i;
    if (i == 2)
      break;
  }
  return data;
}

int main(int argc, char *argv[]) {
  // Declare the supported options.
  po::options_description desc("Allowed options");
  desc.add_options()("help", "produce help message")(
      "depth,d", po::value<double>()->default_value(50.), "trench depth")(
      "width,w", po::value<double>()->default_value(20.), "Trench width")(
      "taper-angle,t", po::value<std::string>()->required(), //->default_value("1., 0."),
      "Normal vector of trench sidewall.");

  // Parse the arguments and catch unknown option and invalid option value
  // exceptions
  po::variables_map vm;
  try {
    po::store(po::parse_command_line(argc, argv, desc), vm);
  } catch (po::unknown_option &e) {
    std::cout << e.what() << std::endl;
    std::cout << desc << std::endl;
    return 1;
  } catch (po::invalid_option_value &e) {
    std::cout << e.what() << std::endl;
    std::cout << desc << std::endl;
    return 1;
  }
  po::notify(vm);

  //
  if (vm.count("help")) {
    std::cout << desc << std::endl;
    return 1;
  }

  if (vm.count("depth")) {
    std::cout << "Compression level was set to " << vm["compression"].as<int>()
              << ".\n";
  }

  if (vm.count("taper-angle")) {
    strToArray(vm["taper-angle"].as<std::string>());
  }

  return 0;

  // omp_set_num_threads(1);

  constexpr int D = 2;
  typedef double NumericType;
  double gridDelta = 1;
  // Process parameters

  double extent = 20;
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

  hrleVectorType<double, 2> center(0., 0.);
  hrleVectorType<double, 2> normSide(1, 0);
  double diameter = 20.;
  double depth = 50.;

  auto substrate = lsSmartPointer<lsDomain<NumericType, D>>::New(
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
    makeTaperedTrench(trenchMesh, center, normSide, diameter, depth);
    lsFromSurfaceMesh<double, D>(trench, trenchMesh, false).apply();
    lsBooleanOperation<double, D>(substrate, trench,
                                  lsBooleanOperationEnum::RELATIVE_COMPLEMENT)
        .apply();
  }

  std::cout << "Saving Geometry" << std::endl;
  auto mesh = lsSmartPointer<lsMesh<>>::New();
  lsToSurfaceMesh<NumericType, D>(substrate, mesh).apply();
  lsVTKWriter(mesh, "trench.vtk").apply();
  // auto volumeMeshingi = lsSmartPointer<lsWriteVisualizationMesh<NumericType,
  // D>>::New(); volumeMeshingi->insertNextLevelSet(substrate);
  // volumeMeshingi->setFileName("volume_i");
  // volumeMeshingi->apply();

  return 0;
}

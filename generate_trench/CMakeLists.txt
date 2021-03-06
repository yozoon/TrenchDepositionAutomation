cmake_minimum_required(VERSION 3.15)

project("GenerateTrench")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

## Enable Clang sanitizer for debug builds
if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address -fsanitize=thread -fsanitize=memory" CACHE STRING "")
  set(CMAKE_EXE_LINKER_FLAGS_DEBUG "${CMAKE_EXE_LINKER_FLAGS_DEBUGS} -fno-omit-frame-pointer -fsanitize=address -fsanitize=thread -fsanitize=memory" CACHE STRING "")
endif()

# set default build type
SET(DEFAULT_BUILD_TYPE "Debug")
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to '${DEFAULT_BUILD_TYPE}' as none was specified.")
  set(CMAKE_BUILD_TYPE "${DEFAULT_BUILD_TYPE}" CACHE
      STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

# automatically append standard path for ViennaHRLEConfig.cmake
# might need to be changed for different install directories
# not necessary when installed to /usr/local (not recommended)
SET(ViennaToolsDir "/home/life/Documents/ViennaTools")
SET(ViennaHRLE_DIR "${ViennaToolsDir}/ViennaHRLE/install/ViennaHRLE/lib/cmake/ViennaHRLE")
SET(ViennaLS_DIR "${ViennaToolsDir}/ViennaLS/install/ViennaLS/lib/cmake/ViennaLS")

find_package(ViennaHRLE REQUIRED)
find_package(ViennaLS REQUIRED)

find_package(Python COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG)

# Python method:
Python_add_library(generate_trench generate_trench.cpp)
target_link_libraries(generate_trench PUBLIC pybind11::headers)
target_include_directories(generate_trench PUBLIC ${VIENNALS_INCLUDE_DIRS})
target_link_libraries(generate_trench PRIVATE ${VIENNALS_LIBRARIES})
set_target_properties(generate_trench PROPERTIES
                              INTERPROCEDURAL_OPTIMIZATION ON
                              CXX_VISIBILITY_PRESET default
                              VISIBLITY_INLINES_HIDDEN ON)

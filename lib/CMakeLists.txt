cmake_minimum_required(VERSION 3.24)

project(
    libgesel
    VERSION 1.0.0
    DESCRIPTION "Building the gesel shared library"
    LANGUAGES CXX
)

# Fetching dependencies.
# At some point we will move to assorthead, but I'm not ready to update all of those libraries yet.
include(FetchContent)

FetchContent_Declare(
  byteme
  GIT_REPOSITORY https://github.com/LTLA/byteme
  GIT_TAG v2.1.4
)

FetchContent_Declare(
  sanisizer
  GIT_REPOSITORY https://github.com/LTLA/sanisizer
  GIT_TAG v0.2.2
)

FetchContent_Declare(
  gesel
  GIT_REPOSITORY https://github.com/gesel-inc/gesel-spec
  GIT_TAG v0.2.0
)

FetchContent_Declare(
  phyper 
  GIT_REPOSITORY https://github.com/libscran/phyper
  GIT_TAG v0.1.2
)

FetchContent_MakeAvailable(byteme)
FetchContent_MakeAvailable(sanisizer)
FetchContent_MakeAvailable(gesel)
FetchContent_MakeAvailable(phyper)

# Setting up the pybind target
find_package(pybind11 CONFIG)
pybind11_add_module(
    libgesel
    src/validate.cpp
    src/init.cpp
    src/compute_enrichment.cpp
)

set_property(TARGET libgesel PROPERTY CXX_STANDARD 17)

target_link_libraries(libgesel PRIVATE gesel::gesel pybind11::pybind11 libscran::phyper)
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(libgesel PRIVATE -Wall -Wpedantic -Wextra)
endif()

find_package(ZLIB)
target_link_libraries(libgesel PRIVATE ZLIB::ZLIB)

set_target_properties(  
    libgesel
    PROPERTIES
    OUTPUT_NAME _lib_gesel
    PREFIX ""
)

#include "pybind11/pybind11.h"

void init_validate(pybind11::module&);
void init_compute_enrichment(pybind11::module&);

PYBIND11_MODULE(_lib_gesel, m) {
    init_validate(m);
    init_compute_enrichment(m);
}


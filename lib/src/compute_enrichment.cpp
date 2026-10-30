#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include <cstdint>
#include <type_traits>

#include "phyper/phyper.hpp"
#include "sanisizer/sanisizer.hpp"

template<typename Input_>
using I = std::remove_cv_t<std::remove_reference_t<Input_> >;

// We use unsigned long long to mitigate the risk of overflow.
pybind11::list compute_enrichment(pybind11::list count, pybind11::list size, unsigned long long universe, unsigned long long present) {
    const auto nsets = count.size();

    auto output = sanisizer::create<pybind11::list>(nsets);
    for (I<decltype(nsets)> i = 0; i < nsets; ++i) {
        const auto cur_count = count[i].cast<unsigned long long>();
        const auto cur_size = size[i].cast<unsigned long long>();
        output[i] = phyper::compute(cur_count, cur_size, universe - cur_size, present, {});
    }

    return output;
}

void init_compute_enrichment(pybind11::module& m) {
    m.def("compute_enrichment", &compute_enrichment);
}

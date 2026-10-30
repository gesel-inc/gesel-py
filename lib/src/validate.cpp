#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "gesel/gesel.hpp"
#include "sanisizer/sanisizer.hpp"

void validate_database_files(std::string db_prefix, int num_genes) {
    gesel::validate_database(db_prefix, sanisizer::Cast(num_genes));
}

int validate_gene_files(std::string gene_prefix, std::optional<pybind11::list> types) {
    if (!types.has_value()) {
        const auto num_genes = gesel::validate_genes(gene_prefix);
        return sanisizer::cast<int>(num_genes);
    } 

    std::vector<std::string> name_types;
    name_types.reserve(types->size());
    for (auto t : *types) {
        name_types.push_back(t.cast<std::string>());
    }

    const auto num_genes = gesel::validate_genes(gene_prefix, name_types);
    return sanisizer::cast<int>(num_genes);
}

void init_validate(pybind11::module& m) {
    m.def("validate_database_files", &validate_database_files);
    m.def("validate_gene_files", &validate_gene_files);
}

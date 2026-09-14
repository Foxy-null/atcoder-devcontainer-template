#include <cassert>
#include <cmath>
#include <iostream>
#include <memory>
#include <string>
#include <absl/container/flat_hash_map.h>
#include <atcoder/all>
#include <boost/dynamic_bitset.hpp>
#include <boost/filesystem.hpp>
#include <boost/version.hpp>
#include <Eigen/Dense>
#include <gmpxx.h>
#include <immer/vector.hpp>
#include <LightGBM/c_api.h>
#include <ortools/linear_solver/linear_solver.h>
#include <range/v3/all.hpp>
#include <ankerl/unordered_dense.h>
#include <z3++.h>

static_assert(BOOST_VERSION == 108800);
static_assert(EIGEN_WORLD_VERSION == 3 && EIGEN_MAJOR_VERSION == 4 && EIGEN_MINOR_VERSION == 0);
static_assert(__GNU_MP_VERSION == 6 && __GNU_MP_VERSION_MINOR == 3 && __GNU_MP_VERSION_PATCHLEVEL == 0);
static_assert(ABSL_LTS_RELEASE_VERSION == 20250512 && ABSL_LTS_RELEASE_PATCH_LEVEL == 1);

int main() {
    absl::flat_hash_map<int, int> absl_map{{1, 7}};
    assert(absl_map.at(1) == 7);
    atcoder::dsu sets(3);
    sets.merge(0, 2);
    assert(sets.same(0, 2) && !sets.same(0, 1));

    boost::dynamic_bitset<> bits(128);
    bits.set(100);
    assert(bits.count() == 1 && bits.test(100));
    assert(boost::filesystem::exists("/"));

    Eigen::Matrix2d matrix;
    matrix << 2, 0, 0, 3;
    assert(matrix.determinant() == 6);
    mpz_class big = mpz_class(1) << 100;
    assert(big.get_str() == "1267650600228229401496703205376");

    immer::vector<int> original;
    auto extended = original.push_back(7);
    assert(original.empty() && extended[0] == 7);
    auto squares = ranges::views::iota(1, 4) | ranges::views::transform([](int x) { return x * x; });
    assert(ranges::accumulate(squares, 0) == 14);
    ankerl::unordered_dense::map<int, int> dense{{1, 7}};
    assert(dense.at(1) == 7);

    double data[] = {1, 2, 2, 3, 3, 4, 4, 5};
    DatasetHandle dataset = nullptr;
    assert(LGBM_DatasetCreateFromMat(data, C_API_DTYPE_FLOAT64, 4, 2, 1,
        "min_data_in_leaf=1 min_data_in_bin=1 verbosity=-1", nullptr, &dataset) == 0);
    int rows = 0;
    assert(LGBM_DatasetGetNumData(dataset, &rows) == 0 && rows == 4);
    assert(LGBM_DatasetFree(dataset) == 0);

    // Exercise the optional solver backends enabled in AtCoder's recipe too.
    for (const char* backend : {"GLOP", "CBC", "CLP", "GLPK_LP", "HIGHS_LP", "SCIP"}) {
        std::unique_ptr<operations_research::MPSolver> solver(
            operations_research::MPSolver::CreateSolver(backend));
        if (!solver) {
            std::cerr << "OR-Tools backend unavailable: " << backend << '\n';
            return 1;
        }
        auto* x = solver->MakeNumVar(0, solver->infinity(), "x");
        auto* upper_bound = solver->MakeRowConstraint(-solver->infinity(), 3);
        upper_bound->SetCoefficient(x, 1);
        auto* objective = solver->MutableObjective();
        objective->SetCoefficient(x, 1);
        objective->SetMaximization();
        const auto status = solver->Solve();
        if (status != operations_research::MPSolver::OPTIMAL) {
            std::cerr << "OR-Tools backend failed: " << backend
                      << " (status " << status << ")\n";
            return 1;
        }
        assert(std::abs(objective->Value() - 3) < 1e-7);
    }

    z3::context context;
    z3::solver solver(context);
    auto x = context.int_const("x");
    solver.add(x > 3 && x < 5);
    assert(solver.check() == z3::sat);
    assert(solver.get_model().eval(x).get_numeral_int() == 4);
    unsigned major, minor, patch, revision;
    Z3_get_version(&major, &minor, &patch, &revision);
    assert(major == 4 && minor == 15 && patch == 2);
    std::cout << "11 libraries OK (including Boost dynamic_bitset and OR-Tools solvers)\n";
}

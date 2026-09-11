#include <cassert>
#include <iostream>
#include <torch/torch.h>
#include <torch/version.h>

static_assert(TORCH_VERSION_MAJOR == 2 && TORCH_VERSION_MINOR == 8 && TORCH_VERSION_PATCH == 0);

int main() {
    auto result = torch::ones({2, 3}, torch::kFloat64) * 2;
    assert(result.sum().item<double>() == 12);
    std::cout << "LibTorch 2.8.0 CPU OK\n";
}

#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
setup-atcoder-user
setup-atcoder-user
verify-atcoder-toolchain
python tests/check-portability.py

test_dir="$(mktemp -d -t atcoder-smoke.XXXXXX)"
trap 'rm -rf -- "$test_dir"' EXIT
mkdir -p "$test_dir/a problem/test"
cd "$test_dir/a problem"
cat > "solution file.cpp" <<'CPP'
#include <atcoder/fenwicktree>
#include <expected>
#include <iostream>

int main() {
    int n;
    std::cin >> n;
    atcoder::fenwick_tree<long long> tree(n);
    for (int i = 0; i < n; ++i) {
        long long value;
        std::cin >> value;
        tree.add(i, value);
    }
    std::expected<long long, int> result = tree.sum(0, n);
    std::cout << *result << '\n';
}
CPP
printf '3\n1 2 3\n' > test/sample-1.in
printf '6\n' > test/sample-1.out
printf '1\n-7\n' > test/sample-2.in
printf '%s\n' '-7' > test/sample-2.out
g++ -std=gnu++23 -O2 -Wall -Wextra "solution file.cpp" -o a.out
oj test -c ./a.out -t 2
g++ -std=gnu++23 -g -O0 "solution file.cpp" -o debug.out
gdb --batch -ex 'break main' -ex 'run < test/sample-1.in' -ex continue ./debug.out > gdb.log 2>&1
grep -q 'Breakpoint 1' gdb.log
grep -q 'exited normally' gdb.log
printf 'Container smoke checks passed: setup, C++23, ACL, samples, GDB.\n'

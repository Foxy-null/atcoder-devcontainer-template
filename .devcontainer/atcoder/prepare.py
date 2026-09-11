"""Adapt the saved AtCoder recipe for a root-owned, memory-limited Docker build."""
import hashlib
from pathlib import Path
import re
import shlex
import tomllib

source = Path(__file__).with_name("gcc.toml")
assert hashlib.sha256(source.read_bytes()).hexdigest() == (
    "76c63a226f4fa45511bd62823e7a9ff7bc5a481d04e07371b0d09a7beb752855"
), "The upstream recipe changed; review it before updating the checksum."
recipe = tomllib.loads(source.read_text(encoding="utf-8"))
assert recipe["display"] == "C++23 (GCC 15.2.0)"
assert "-flto" not in recipe["compile"]

script = recipe["install"]
script = script.replace('PARALLEL="$(($(nproc)+2))"', 'PARALLEL="${BUILD_JOBS:-2}"')
# Docker builds run as root. Retain CMAKE_BUILD_PARALLEL_LEVEL in the environment.
script = script.replace("sudo ", "")
script = script.replace(
    "http://ftp.tsukuba.wide.ad.jp/", "https://ftp.tsukuba.wide.ad.jp/"
)
script = script.replace("wget ", "wget --timeout=30 --tries=3 ")
script = script.replace(
    "./contrib/download_prerequisites\n",
    "sed -i 's|http://gcc.gnu.org/pub/gcc/infrastructure/|"
    "https://ftp.tsukuba.wide.ad.jp/software/gcc/infrastructure/|g' "
    "./contrib/download_prerequisites\n./contrib/download_prerequisites\n",
)
# Dependencies are installed in earlier Docker layers; do not rebuild them for OR-Tools.
for name in ("abseil", "eigen"):
    pattern = rf"if \[\[ \$\{{AC_NO_BUILD_{name}:-false\}}.*?exit 0;?\s*fi"
    script, count = re.subn(
        pattern, f'if "${{AC_NO_BUILD_{name}:-false}}";then exit 0;fi',
        script, count=1, flags=re.DOTALL,
    )
    assert count == 1, name
Path("/tmp/install-atcoder.sh").write_text(script, encoding="utf-8")

prefix = Path("/opt/atcoder/gcc")
share = prefix / "share/atcoder"
share.mkdir(parents=True, exist_ok=True)
array = recipe["compile"].split("USER_BUILD_FLAGS=(\n", 1)[1].split(")\nset -eu", 1)[0]
flags = shlex.split(array.replace("::install_dir::", str(prefix)))
compile_flags = [flag for flag in flags if not flag.startswith("-l")]
link_flags = [flag for flag in flags if flag.startswith("-l")]
(share / "flags.sh").write_text(
    "COMPILE_FLAGS=(" + shlex.join(compile_flags) + ")\n"
    "LINK_FLAGS=(" + shlex.join(link_flags) + ")\n", encoding="utf-8",
)
(share / "versions.txt").write_text(
    recipe["display"] + "\n" + "\n".join(
        f"{name} {library['version']}"
        for name, library in recipe["library"].items() if "version" in library
    ) + "\n", encoding="utf-8",
)

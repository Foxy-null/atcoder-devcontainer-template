"""Run from the repository root with Python 3 and Bash; no network calls."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
BASH = os.environ.get("BASH_FOR_TESTS") or shutil.which("bash")
assert BASH, "Bash is required (WSL, Git Bash, or the dev container)."

def run(args, **kwargs):
    return subprocess.run(args, check=True, text=True, encoding="utf-8", capture_output=True, **kwargs)

def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

for file in ROOT.rglob("*.json"):
    if ".git" not in file.parts and file.name != "session.json":
        json.loads(file.read_text(encoding="utf-8"))

dev = read_json(".devcontainer/devcontainer.json")
assert "build" not in dev
assert re.fullmatch(r"ghcr\.io/foxy-null/atcoder-devcontainer-template@sha256:[0-9a-f]{64}", dev["image"])
prebuilt = (ROOT / ".devcontainer/Dockerfile.prebuilt").read_text()
assert prebuilt.splitlines()[0] == f'FROM {dev["image"]}', "Compose and Dev Containers must use the same image"
assert dev["containerEnv"]["ATCODER_REPOSITORY_CONFIG_DIR"] == "${containerWorkspaceFolder}/config"
assert all("${devcontainerId}" in mount for mount in dev["mounts"])
assert "workbench.colorTheme" not in dev["customizations"]["vscode"]["settings"]
extensions = dev["customizations"]["vscode"]["extensions"]
assert "-GitHub.copilot" in extensions and "-GitHub.copilot-chat" in extensions
vscode_settings = read_json(".vscode/settings.json")
assert vscode_settings["chat.disableAIFeatures"] is True
assert vscode_settings["github.copilot.enable"] == {"*": False}
assert vscode_settings["github.copilot.nextEditSuggestions.enabled"] is False
assert read_json(".vscode/c_cpp_properties.json")["configurations"][0]["cppStandard"] == "c++23"
cpp = read_json(".vscode/c_cpp_properties.json")["configurations"][0]
settings = dev["customizations"]["vscode"]["settings"]
for field in ("compilerPath", "includePath", "defines"):
    assert cpp[field] == settings[f"C_Cpp.default.{field}"]
assert cpp["compilerPath"] == "/opt/atcoder/gcc/bin/g++"
recipe = tomllib.loads((ROOT / ".devcontainer/atcoder/gcc.toml").read_text(encoding="utf-8"))
assert recipe["display"] == "C++23 (GCC 15.2.0)"
assert "-flto" not in recipe["compile"]
assert len([lib for lib in recipe["library"].values() if "version" in lib]) == 12
for directory in (".devcontainer", ".vscode", "config"):
    for file in (ROOT / directory).rglob("*"):
        if file.name not in ("session.json", "cookie.jar") and file.is_file():
            content = file.read_text(encoding="utf-8")
            assert "/home/foxy_null" not in content, file
            assert "/workspaces/AtCoder" not in content, file
            assert "uninstall-extension" not in content, file

for script in (ROOT / ".devcontainer/scripts").iterdir():
    assert b"\r" not in script.read_bytes(), script
    run([BASH, "-n", str(script)])
run([BASH, str(ROOT / ".devcontainer/scripts/atcoder-workflow"), "self-test"])
tasks = {task["label"]: task for task in read_json(".vscode/tasks.json")["tasks"]}
for task in tasks.values():
    if task["command"] == "bash":
        run([BASH, "-n", "-c", task["args"][1]])

with tempfile.TemporaryDirectory(prefix="atcoder portability ") as temp:
    work = Path(temp)
    repo = work / "another user's repository"
    repo.mkdir()
    log = work / "arguments"
    acc_config = work / "another user's config"
    (acc_config / "cpp").mkdir(parents=True)
    (acc_config / "cpp/main.cpp").write_text("template\n", encoding="utf-8")
    mock = work / "mock-tools.sh"
    mock.write_text(
        'atcoder-g++() { printf "%s\\0" "$@" > "$CHECK_LOG"; }\n'
        'oj() { printf "%s\\0" "$@" > "$OJ_LOG"; }\n'
        'code() { :; }\n'
        'acc() { printf "%s\\n" "$ACC_TEST_CONFIG"; }\n',
        encoding="utf-8", newline="\n"
    )
    env = {
        **os.environ, "BASH_ENV": mock.as_posix(),
        "CHECK_LOG": log.as_posix(), "OJ_LOG": (work / "oj-arguments").as_posix(),
        "ACC_TEST_CONFIG": acc_config.as_posix(),
        "MSYS_NO_PATHCONV": "1",
    }

    def task_run(label, substitutions, cwd=repo, check=True):
        task = tasks[label]
        assert task["type"] == "process"
        args = [substitutions.get(arg, arg) for arg in task["args"]]
        command = BASH if task["command"] == "bash" else task["command"]
        result = subprocess.run([command, *args], cwd=cwd, env=env, text=True,
                                encoding="utf-8", capture_output=True)
        if check:
            assert result.returncode == 0, result.stderr
        return result

    solution = repo / "source $(touch INJECTED).cpp"
    solution.write_text("int main() {}\n", encoding="utf-8")
    task_run("build & test", {"${file}": solution.as_posix()})
    arguments = log.read_bytes().decode().split("\0")[:-1]
    assert solution.as_posix() in arguments, arguments
    assert arguments == [solution.as_posix(), "-o", "a.out"], arguments
    assert not (repo / "INJECTED").exists()
    debug = tasks["build for debug"]
    assert debug["type"] == "process" and debug["command"] == "atcoder-g++"
    assert "-g" in debug["args"] and "-O0" in debug["args"]
    assert debug["options"]["cwd"] == "${fileDirname}"

    values = {"${input:yukicoder problem}": "3412", "${workspaceFolder}": repo.as_posix()}
    task_run("Download from yukicoder", values)
    downloaded = repo / "yukicoder/3412/main.cpp"
    assert downloaded.read_text() == "template\n"
    downloaded.write_text("my edited solution\n", encoding="utf-8")
    task_run("Download from yukicoder", values)
    assert downloaded.read_text() == "my edited solution\n"
    values["${input:yukicoder problem}"] = "../escape; touch INJECTED"
    failed = task_run("Download from yukicoder", values, check=False)
    assert failed.returncode != 0
    assert not (repo / "INJECTED").exists()

    task_run("submit to yukicoder (C++)", {"${file}": downloaded.as_posix()},
             cwd=downloaded.parent)
    oj_args = (work / "oj-arguments").read_bytes().decode().split("\0")[:-1]
    assert oj_args == ["submit", "https://yukicoder.me/problems/no/3412", downloaded.as_posix()]

dockerignore = (ROOT / ".dockerignore").read_text()
assert "**/session.json" in dockerignore and "**/cookie.jar" in dockerignore
dockerfile = (ROOT / ".devcontainer/Dockerfile").read_text()
assert "COPY config/atcoder-cli /" not in dockerfile
assert "vscode-extensions" not in dockerfile
workflow = (ROOT / ".github/workflows/publish-devcontainer.yml").read_text()
action_refs = re.findall(r"^\s*uses:\s*\S+@(\S+)\s*$", workflow, re.MULTILINE)
assert action_refs and all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs)
assert "github.repository == 'Foxy-null/atcoder-devcontainer-template'" in workflow
assert '"${IMAGE_NAME}:candidate"' in workflow
assert '"${IMAGE_NAME}:stable"' in workflow
assert "github.ref == 'refs/heads/main'" in workflow
assert "--cpus=2" in workflow and "--memory=4g" in workflow
assert "create-storage-record: false" in workflow
install_stage = (ROOT / ".devcontainer/atcoder/install-stage").read_text()
assert "for component in COMPILER " in install_stage
assert "component=COMPILER" in install_stage
print("Portability checks passed (mocked tools; container build not tested).")

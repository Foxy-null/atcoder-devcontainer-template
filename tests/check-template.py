"""Linux regression checks using real acc 2.2.0; no AtCoder access or credentials."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ACC = shutil.which("acc")
assert ACC, "Install atcoder-cli@2.2.0 before running this test."

with tempfile.TemporaryDirectory(prefix="atcoder template '") as temp:
    work = Path(temp)
    repo = work / "repository"
    template_dir = repo / "config/atcoder-cli/cpp"
    template_dir.mkdir(parents=True)
    template = template_dir / "main.cpp"
    template.write_text("template-v1\n")
    shutil.copyfile(ROOT / "config/atcoder-cli/cpp/template.json", template_dir / "template.json")
    # Catch accidental writes through the new directory link on repeat setup.
    (template_dir / "Makefile").write_text("user Makefile\n")
    tools = work / "tools"
    tools.mkdir()

    def executable(path, script):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/bin/sh\n" + script + "\n")
        path.chmod(0o755)

    executable(tools / "oj", "exit 0")
    executable(work / "pipx/venvs/online-judge-tools/bin/python",
               'printf "%s\\n" "$TEST_COOKIE"')
    env = {**os.environ, "HOME": str(work / "home"),
           "XDG_CONFIG_HOME": str(work / "config"), "NO_UPDATE_NOTIFIER": "1",
           "PATH": f"{tools}:{os.environ['PATH']}",
           "PIPX_HOME": str(work / "pipx"), "TEST_COOKIE": str(work / "oj/cookie.jar"),
           "ATCODER_REPOSITORY_CONFIG_DIR": str(repo / "config"),
           "ATCODER_CONFIG_SOURCE_DIR": str(ROOT / "config/atcoder-cli")}

    def run(*args, cwd=repo, ok=True):
        result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
        if ok:
            assert result.returncode == 0, result.stdout + result.stderr
        return result

    assert run(ACC, "--version").stdout.strip() == "2.2.0"
    config = Path(run(ACC, "config-dir").stdout.strip())
    assert config.is_relative_to(work), config
    old = config / "cpp"
    old.mkdir(parents=True)
    (old / "main.cpp").write_text("custom old template\n")
    (old / "custom.txt").write_text("keep me\n")
    setup = ROOT / ".devcontainer/scripts/setup-atcoder-user"
    run("bash", str(setup))
    assert old.is_symlink() and old.resolve() == template_dir
    assert not (old / "main.cpp").is_symlink()
    backups = list(config.glob("cpp.backup.*/cpp"))
    assert len(backups) == 1
    assert (backups[0] / "main.cpp").read_text() == "custom old template\n"
    assert (backups[0] / "custom.txt").read_text() == "keep me\n"
    # Both template.json and Makefile remain user-controlled on subsequent setup.
    template_json = template_dir / "template.json"
    template_json.write_text(json.dumps({"task": {"program": ["main.cpp"], "submit": "main.cpp"}}, indent=4))
    settings = template_json.read_bytes()
    run("bash", str(setup))
    assert template_json.read_bytes() == settings
    assert (template_dir / "Makefile").read_text() == "user Makefile\n"
    assert len(list(config.glob("cpp.backup.*"))) == 1

    def contest(name):
        folder = repo / "atcoder/ABC" / name
        folder.mkdir(parents=True)
        url = f"https://atcoder.jp/contests/{name}"
        data = {"contest": {"id": name, "title": name, "url": url}, "tasks": [
            {"id": f"{name}_{label}", "label": label.upper(), "title": label,
             "url": f"{url}/tasks/{name}_{label}"} for label in ("a", "b")]}
        (folder / "contest.acc.json").write_text(json.dumps(data))
        return folder

    def add(folder):
        run(ACC, "add", "--choice", "all", "--force", "--no-tests", cwd=folder)
        for label in ("a", "b"):
            answer = folder / label / "main.cpp"
            assert answer.is_file() and not answer.is_symlink(), answer
        manifest = json.loads((folder / "contest.acc.json").read_text())
        assert all(t["directory"]["submit"] == "main.cpp" for t in manifest["tasks"])

    first, second = contest("abc475"), contest("abc476")
    add(first)
    add(second)
    answer = first / "a/main.cpp"
    answer.write_text("solution-A\n")
    assert template.read_text() == "template-v1\n"
    assert (first / "b/main.cpp").read_text() == "template-v1\n"
    assert (second / "a/main.cpp").read_text() == "template-v1\n"
    template.write_text("template-v2\n")
    third = contest("abc477")
    add(third)
    assert (third / "a/main.cpp").read_text() == "template-v2\n"
    add(first)
    assert answer.read_text() == "solution-A\n"
    assert (first / "b/main.cpp").read_text() == "template-v1\n"

    # Same source, ordinary cp path used by the yukicoder task.
    copied = repo / "yukicoder.cpp"
    run("cp", "--", str(old / "main.cpp"), str(copied))
    assert not copied.is_symlink() and copied.read_bytes() == template.read_bytes()

    legacy = second / "a/main.cpp"
    legacy.unlink()
    legacy.symlink_to(template)
    relative = second / "b/main.cpp"
    relative.unlink()
    relative.symlink_to(os.path.relpath(template, relative.parent))
    unknown = third / "a/main.cpp"
    unknown.unlink()
    unknown.symlink_to(answer)
    broken = third / "b/main.cpp"
    broken.unlink()
    broken.symlink_to(work / "missing.cpp")
    outside = work / "outside"
    outside.mkdir()
    (outside / "main.cpp").symlink_to(template)
    (repo / "atcoder/outside").symlink_to(outside, target_is_directory=True)
    migrate = ROOT / ".devcontainer/atcoder/migrate-solution-links.py"
    preview = run("python3", str(migrate), str(repo), ok=False)
    assert preview.returncode == 1 and "Eligible: 2; skipped links: 2" in preview.stdout
    assert legacy.is_symlink() and not list(repo.glob(".solution-link-backup-*"))
    applied = run("python3", str(migrate), str(repo), "--apply", ok=False)
    assert applied.returncode == 1 and "Detached: 2; skipped links: 2" in applied.stdout
    assert not legacy.is_symlink() and not relative.is_symlink()
    assert legacy.read_text() == relative.read_text() == "template-v2\n"
    assert unknown.is_symlink() and broken.is_symlink()
    assert (outside / "main.cpp").is_symlink()
    snapshots = list(repo.glob(".solution-link-backup-*"))
    assert len(snapshots) == 1
    records = json.loads((snapshots[0] / "links.json").read_text())
    assert len(records) == 2
    assert all((snapshots[0] / r["path"]).read_text() == "template-v2\n" for r in records)
    legacy.write_text("independent legacy answer\n")
    assert template.read_text() == relative.read_text() == "template-v2\n"
    again = run("python3", str(migrate), str(repo), "--apply", ok=False)
    assert "Detached: 0; skipped links: 2" in again.stdout
    assert len(list(repo.glob(".solution-link-backup-*"))) == 1
    assert answer.read_text() == "solution-A\n"

    # Unexpected directory links and file-link templates fail closed.
    old.unlink()
    old.symlink_to(outside, target_is_directory=True)
    assert run("bash", str(setup), ok=False).returncode != 0
    assert old.resolve() == outside
    old.unlink()
    template.unlink()
    template.symlink_to(answer)
    assert run("bash", str(setup), ok=False).returncode != 0

print("Template checks passed: real acc, independent answers, repeat setup, safe legacy migration.")

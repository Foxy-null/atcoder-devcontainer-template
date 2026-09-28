#!/usr/bin/env python3
"""Preview or detach legacy answer symlinks without changing their contents."""
import argparse
import json
import os
from pathlib import Path
import stat
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--apply", action="store_true", help="back up and replace matching links")
    args = parser.parse_args()
    workspace = args.workspace.resolve(strict=True)
    template = workspace / "config/atcoder-cli/cpp/main.cpp"
    if template.is_symlink() or not template.is_file():
        parser.error(f"Expected a regular template file: {template}")
    answers = workspace / "atcoder"
    if answers.is_symlink():
        parser.error(f"Refusing to traverse a linked answer directory: {answers}")

    candidates = []
    skipped = 0
    # Do not traverse directory links, including those pointing outside the workspace.
    for directory, _, files in os.walk(answers, followlinks=False):
        if "main.cpp" not in files:
            continue
        answer = Path(directory) / "main.cpp"
        if not answer.is_symlink():
            continue
        try:
            target = answer.resolve(strict=True)
        except (OSError, RuntimeError):
            target = None
        if target != template:
            print(f"SKIP (unknown or broken link): {answer}")
            skipped += 1
            continue
        candidates.append((answer, os.readlink(answer)))
        print(f"{'DETACH' if args.apply else 'WOULD DETACH'}: {answer}")

    if args.apply and candidates:
        backup = Path(tempfile.mkdtemp(prefix=".solution-link-backup-", dir=workspace))
        print(f"Backup: {backup}", flush=True)
        # Back up every candidate before changing any link.
        records = []
        for answer, link in candidates:
            relative = answer.relative_to(workspace)
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(answer.read_bytes())
            records.append({"path": relative.as_posix(), "link": link})
        (backup / "links.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

        for answer, link in candidates:
            content = (backup / answer.relative_to(workspace)).read_bytes()
            if not answer.is_symlink() or os.readlink(answer) != link or answer.read_bytes() != content:
                raise RuntimeError(f"Answer changed during migration; backup retained: {answer}")
            mode = stat.S_IMODE(answer.stat().st_mode)
            fd, temporary = tempfile.mkstemp(prefix=".main.cpp-", dir=answer.parent)
            try:
                with os.fdopen(fd, "wb") as output:
                    output.write(content)
                    os.fchmod(output.fileno(), mode)
                os.replace(temporary, answer)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
    print(f"{'Detached' if args.apply else 'Eligible'}: {len(candidates)}; skipped links: {skipped}")
    return 1 if skipped else 0


if __name__ == "__main__":
    raise SystemExit(main())

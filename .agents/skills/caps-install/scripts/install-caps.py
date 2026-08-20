#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = "https://github.com/Mutoy-choi/CAPS-Agent-Security.git"
DEFAULT_DESTINATION = Path.home() / ".local" / "share" / "caps-unlock-lab"


def run(args: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def confirm(message: str, assume_yes: bool) -> None:
    if assume_yes:
        return
    if input(f"{message} [y/N] ").strip().lower() not in {"y", "yes"}:
        raise SystemExit("Installation cancelled.")


def clone_or_update(repo: str, ref: str, destination: Path, assume_yes: bool) -> None:
    if destination.exists():
        if not (destination / ".git").exists():
            raise SystemExit(f"Destination exists but is not a git repository: {destination}")
        confirm(f"Update {destination} from {repo}?", assume_yes)
        run(["git", "fetch", "--depth", "1", "origin", ref], cwd=destination)
        run(["git", "checkout", ref], cwd=destination)
        run(["git", "pull", "--ff-only", "origin", ref], cwd=destination)
        return
    confirm(f"Clone {repo} ({ref}) into {destination}?", assume_yes)
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--depth", "1", "--branch", ref, repo, str(destination)])


def main() -> int:
    parser = argparse.ArgumentParser(description="Install CAPS Unlock Lab components")
    parser.add_argument("--component", choices=("verify", "chat", "all"), default="verify")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--ref", default="main")
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()

    if shutil.which("git") is None:
        raise SystemExit("git is required")
    destination = args.destination.expanduser()
    clone_or_update(args.repo, args.ref, destination, args.yes)

    if args.component in {"verify", "all"}:
        venv = destination / ".venv"
        run([sys.executable, "-m", "venv", str(venv)])
        python = venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
        run([str(python), "-m", "pip", "install", "-e", f"{destination / 'caps_verify'}[gateway]"])
        print(f"CAPS Verify installed. CLI directory: {python.parent}")
    if args.component in {"chat", "all"}:
        if shutil.which("docker") is None:
            print("Docker is required before starting CAPS Research Chat.")
        print(f"Run ./bootstrap.sh in {destination / 'caps_app'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

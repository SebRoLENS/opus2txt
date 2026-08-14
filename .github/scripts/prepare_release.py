#!/usr/bin/env python3
"""Prepare metadata for an automatic opus2txt release."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "opus2txt.py"
README = ROOT / "README.md"
MANUAL = ROOT / "MANUAL.md"
CITATION = ROOT / "CITATION.cff"

VERSION_RE = re.compile(r'^__version__\s*=\s*"(\d+\.\d+\.\d+)"', re.M)
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
MANUAL_VERSION_RE = re.compile(
    r"^\*\*Current manual version:\s*(\d+\.\d+\.\d+)\*\*$", re.M
)
VERSION_BADGE_RE = re.compile(
    r"^\[!\[(?:Latest release|Version)\]\([^)]+\)\]\([^)]+\)[ \t]*$", re.M
)
DOI_BADGE_RE = re.compile(
    r"^\[!\[DOI\]\([^)]+\)\]\([^)]+\)[ \t]*$", re.M
)

VERSION_BADGE = (
    "[![Version](https://img.shields.io/github/v/release/SebRoLENS/opus2txt)]"
    "(https://github.com/SebRoLENS/opus2txt/releases/latest)"
)
DOI_PENDING_BADGE = (
    "[![DOI](https://img.shields.io/badge/DOI-pending-lightgrey)]"
    "(https://github.com/SebRoLENS/opus2txt/releases/latest)"
)


def read_version(text: str) -> str:
    match = VERSION_RE.search(text)
    if not match:
        raise SystemExit("Could not find __version__ in opus2txt.py")
    return match.group(1)


def git_previous_script() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "show", "HEAD^:opus2txt.py"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None


def tuple_version(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.fullmatch(version)
    if not match:
        raise SystemExit(f"Unsupported version format: {version}")
    return tuple(map(int, match.groups()))


def choose_version() -> tuple[str, str]:
    current = read_version(SCRIPT.read_text())
    previous_text = git_previous_script()
    previous = read_version(previous_text) if previous_text else current

    # Respect an explicit manual version bump in the user's source commit.
    if current != previous:
        if tuple_version(current) <= tuple_version(previous):
            raise SystemExit(
                f"Manual version {current} must be newer than previous version {previous}"
            )
        return previous, current

    major, minor, patch = tuple_version(current)
    return current, f"{major}.{minor}.{patch + 1}"


def replace_section(text: str, heading: str, next_heading: str, body: str) -> str:
    pattern = re.compile(
        rf"(?ms)^{re.escape(heading)}\n.*?(?=^{re.escape(next_heading)}\n)"
    )
    if not pattern.search(text):
        raise SystemExit(f"Could not find README section {heading!r}")
    return pattern.sub(body.rstrip() + "\n\n", text, count=1)


def update_badges_for_pending_doi(text: str) -> str:
    if VERSION_BADGE_RE.search(text):
        text = VERSION_BADGE_RE.sub(VERSION_BADGE, text, count=1)
    else:
        title = "# opus2txt\n"
        if title not in text:
            raise SystemExit("Could not find opus2txt README title")
        text = text.replace(title, title + "\n" + VERSION_BADGE + "\n", 1)

    if DOI_BADGE_RE.search(text):
        text = DOI_BADGE_RE.sub(DOI_PENDING_BADGE, text, count=1)
    else:
        text = text.replace(VERSION_BADGE, VERSION_BADGE + "\n" + DOI_PENDING_BADGE, 1)
    return text


def update_readme(old_version: str, new_version: str) -> None:
    text = README.read_text()
    text = text.replace(old_version, new_version)
    text = update_badges_for_pending_doi(text)

    citation = f"""## How to cite

If opus2txt contributes to published research, please acknowledge or cite the software. GitHub also provides a **Cite this repository** entry from [`CITATION.cff`](CITATION.cff).

Version **{new_version}** is archived automatically on Zenodo after the GitHub release is published. The DOI for this release is being assigned and will be inserted here automatically.

> Romi, S. (2026). *opus2txt* (Version {new_version}) [Computer software]. GitHub. https://github.com/SebRoLENS/opus2txt/releases/tag/v{new_version}

Previous releases remain archived separately on Zenodo.
"""
    text = replace_section(text, "## How to cite", "## License", citation)
    README.write_text(text)


def update_manual(new_version: str) -> None:
    text = MANUAL.read_text()
    replacement = f"**Current manual version: {new_version}**"
    if MANUAL_VERSION_RE.search(text):
        text = MANUAL_VERSION_RE.sub(replacement, text, count=1)
    else:
        title = "# opus2txt User Manual\n"
        if title not in text:
            raise SystemExit("Could not find opus2txt manual title")
        text = text.replace(title, title + "\n" + replacement + "\n", 1)
    MANUAL.write_text(text)


def update_citation(new_version: str) -> None:
    text = CITATION.read_text()
    text = re.sub(r"^doi:\s*.*\n", "", text, flags=re.M)
    text = re.sub(
        r'^url:\s*.*$',
        f'url: "https://github.com/SebRoLENS/opus2txt/releases/tag/v{new_version}"',
        text,
        flags=re.M,
    )
    text = re.sub(
        r'^version:\s*.*$', f'version: "{new_version}"', text, flags=re.M
    )
    text = re.sub(
        r"^date-released:\s*.*$",
        f"date-released: {dt.date.today().isoformat()}",
        text,
        flags=re.M,
    )
    CITATION.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version-only", action="store_true")
    args = parser.parse_args()

    old_version, new_version = choose_version()
    if args.version_only:
        print(new_version)
        return

    script_text = SCRIPT.read_text()
    script_text = VERSION_RE.sub(
        f'__version__ = "{new_version}"', script_text, count=1
    )
    SCRIPT.write_text(script_text)
    update_readme(old_version, new_version)
    update_manual(new_version)
    update_citation(new_version)
    print(new_version)


if __name__ == "__main__":
    main()

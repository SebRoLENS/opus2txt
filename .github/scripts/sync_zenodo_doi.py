#!/usr/bin/env python3
"""Find the Zenodo DOI for an opus2txt release and update project metadata."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "opus2txt.py"
README = ROOT / "README.md"
CITATION = ROOT / "CITATION.cff"

VERSION_RE = re.compile(r'^__version__\s*=\s*"(\d+\.\d+\.\d+)"', re.M)
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


def current_version() -> str:
    match = VERSION_RE.search(SCRIPT.read_text())
    if not match:
        raise SystemExit("Could not find __version__")
    return match.group(1)


def version_matches(value: object, wanted: str) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return text == wanted or text == f"v{wanted}"


def extract_doi(record: dict) -> str | None:
    pids = record.get("pids") or {}
    doi = pids.get("doi") if isinstance(pids, dict) else None
    if isinstance(doi, dict) and doi.get("identifier"):
        return str(doi["identifier"])
    if isinstance(doi, str):
        return doi
    if record.get("doi"):
        return str(record["doi"])
    metadata = record.get("metadata") or {}
    if metadata.get("doi"):
        return str(metadata["doi"])
    return None


def zenodo_records(query: str) -> list[dict]:
    # Zenodo limits unauthenticated requests to at most 25 records per page.
    params = urllib.parse.urlencode({"q": query, "size": 25})
    url = f"https://zenodo.org/api/records?{params}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "opus2txt-release-bot/1.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "replace").strip()
        except Exception:
            pass
        message = f"Zenodo API request failed with HTTP {exc.code}"
        if detail:
            message += f": {detail}"
        raise RuntimeError(message) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Zenodo API request failed: {exc}") from exc

    return ((payload.get("hits") or {}).get("hits") or [])


def find_doi(version: str) -> str | None:
    queries = [
        '"opus2txt"',
        f'"opus2txt" AND "{version}"',
        version,
    ]

    candidates: list[dict] = []
    seen_ids: set[str] = set()
    last_error: RuntimeError | None = None

    for query in queries:
        try:
            hits = zenodo_records(query)
        except RuntimeError as exc:
            last_error = exc
            continue

        for record in hits:
            record_id = str(record.get("id") or "")
            if record_id and record_id in seen_ids:
                continue
            if record_id:
                seen_ids.add(record_id)

            metadata = record.get("metadata") or {}
            if str(metadata.get("title", "")).strip().lower() != "opus2txt":
                continue
            if not version_matches(metadata.get("version"), version):
                continue
            if extract_doi(record):
                candidates.append(record)

    if not candidates:
        if last_error is not None:
            raise last_error
        return None

    candidates.sort(
        key=lambda record: str(record.get("updated") or record.get("created") or ""),
        reverse=True,
    )
    return extract_doi(candidates[0])


def replace_section(text: str, heading: str, next_heading: str, body: str) -> str:
    pattern = re.compile(
        rf"(?ms)^{re.escape(heading)}\n.*?(?=^{re.escape(next_heading)}\n)"
    )
    if not pattern.search(text):
        raise SystemExit(f"Could not find README section {heading!r}")
    return pattern.sub(body.rstrip() + "\n\n", text, count=1)


def set_readme_badges(text: str, doi: str) -> str:
    doi_url = f"https://doi.org/{doi}"
    doi_badge = f"[![DOI](https://zenodo.org/badge/DOI/{doi}.svg)]({doi_url})"

    if VERSION_BADGE_RE.search(text):
        text = VERSION_BADGE_RE.sub(VERSION_BADGE, text, count=1)
    else:
        title = "# opus2txt\n"
        if title not in text:
            raise SystemExit("Could not find opus2txt README title")
        text = text.replace(title, title + "\n" + VERSION_BADGE + "\n", 1)

    if DOI_BADGE_RE.search(text):
        text = DOI_BADGE_RE.sub(doi_badge, text, count=1)
    else:
        text = text.replace(VERSION_BADGE, VERSION_BADGE + "\n" + doi_badge, 1)
    return text


def apply_metadata(version: str, doi: str) -> None:
    doi_url = f"https://doi.org/{doi}"

    readme = README.read_text()
    readme = set_readme_badges(readme, doi)

    citation = f"""## How to cite

If opus2txt contributes to published research, please acknowledge or cite the software. GitHub also provides a **Cite this repository** entry from [`CITATION.cff`](CITATION.cff).

> Romi, S. (2026). *opus2txt* (Version {version}) [Computer software]. Zenodo. {doi_url}

DOI: [**{doi}**]({doi_url})

Previous releases remain archived separately on Zenodo.
"""
    readme = replace_section(readme, "## How to cite", "## License", citation)
    README.write_text(readme)

    cff = CITATION.read_text()
    cff = re.sub(r"^doi:\s*.*\n", "", cff, flags=re.M)
    cff = re.sub(r'^version:\s*.*$', f'version: "{version}"', cff, flags=re.M)
    cff = re.sub(r'^url:\s*.*$', f'url: "{doi_url}"', cff, flags=re.M)

    lines = cff.splitlines()
    repository_index = next(
        (index + 1 for index, line in enumerate(lines) if line.startswith("repository-code:")),
        None,
    )
    if repository_index is None:
        raise SystemExit("Could not find repository-code in CITATION.cff")
    lines.insert(repository_index, f'doi: "{doi}"')
    CITATION.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=None)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    version = args.version or current_version()
    try:
        doi = find_doi(version)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(3)

    if not doi:
        print(f"Zenodo DOI for v{version} not found yet.", file=sys.stderr)
        raise SystemExit(2)

    if args.apply:
        apply_metadata(version, doi)
    print(doi)


if __name__ == "__main__":
    main()

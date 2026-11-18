"""Maintain the DOI badge in centered HTML and legacy Markdown README headers."""

import re

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
HTML_DOI_BADGE_RE = re.compile(r'<a href="[^"]*"><img src="[^"]*" alt="DOI"></a>')


def set_readme_badges(text: str, doi: str | None = None) -> str:
    if doi:
        target = f"https://doi.org/{doi}"
        image = f"https://zenodo.org/badge/DOI/{doi}.svg"
    else:
        target = "https://github.com/SebRoLENS/opus2txt/releases/latest"
        image = "https://img.shields.io/badge/DOI-pending-lightgrey"

    if HTML_DOI_BADGE_RE.search(text):
        badge = f'<a href="{target}"><img src="{image}" alt="DOI"></a>'
        return HTML_DOI_BADGE_RE.sub(badge, text, count=1)

    doi_badge = f"[![DOI]({image})]({target})"
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

#!/usr/bin/env python3
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"Could not find expected block: {label}")
    return text.replace(old, new, 1)


path = Path("opus2txt.py")
text = path.read_text()

text = replace_once(
    text,
    """import io
import json
import os
import sys
""",
    """import io
import json
import os
import subprocess
import sys
""",
    "imports",
)

text = replace_once(
    text,
    """MANUAL_URL = "https://github.com/SebRoLENS/opus2txt/blob/main/MANUAL.md"
GITHUB_URL = "https://github.com/SebRoLENS/opus2txt"
""",
    """MANUAL_URL = "https://github.com/SebRoLENS/opus2txt/blob/main/MANUAL.md"
GITHUB_URL = "https://github.com/SebRoLENS/opus2txt"
CONTACT_EMAIL = "romi@lens.unifi.it"
""",
    "constants",
)

helper = '''

def _clean_external_environment() -> dict[str, str]:
    """Remove frozen-app variables that can break external browser launchers."""
    env = os.environ.copy()
    if sys.platform.startswith("linux"):
        original = env.pop("LD_LIBRARY_PATH_ORIG", None)
        if original is None:
            env.pop("LD_LIBRARY_PATH", None)
        else:
            env["LD_LIBRARY_PATH"] = original
        for key in (
            "PYTHONHOME",
            "PYTHONPATH",
            "QT_PLUGIN_PATH",
            "QT_QPA_PLATFORM_PLUGIN_PATH",
            "QML2_IMPORT_PATH",
        ):
            env.pop(key, None)
    elif sys.platform == "darwin":
        env.pop("DYLD_LIBRARY_PATH", None)
        env.pop("DYLD_FALLBACK_LIBRARY_PATH", None)
    return env


def open_external_url(parent: QWidget, url: str) -> None:
    """Open a URL with the operating system and show the explicit URL on failure."""
    try:
        if sys.platform == "win32":
            os.startfile(url)  # type: ignore[attr-defined]
            return

        env = _clean_external_environment()
        commands = [["open", url]] if sys.platform == "darwin" else [
            ["xdg-open", url],
            ["gio", "open", url],
        ]

        last_error: Exception | None = None
        for command in commands:
            try:
                result = subprocess.run(
                    command,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                    check=False,
                )
            except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
                last_error = exc
                continue
            if result.returncode == 0:
                return
            last_error = RuntimeError(
                f"{command[0]} exited with code {result.returncode}"
            )
        raise last_error or RuntimeError("No URL opener is available")
    except Exception:
        QMessageBox.warning(
            parent,
            "Could not open link",
            "The link could not be opened automatically.\\n\\n"
            "If this does not work, copy this link into your browser:\\n\\n"
            f"{url}",
        )
'''

text = replace_once(
    text,
    "\n\ndef has_dot_hidden_component(path: str | Path) -> bool:",
    helper + "\n\ndef has_dot_hidden_component(path: str | Path) -> bool:",
    "URL helper insertion point",
)

text = replace_once(
    text,
    """        links.setTextFormat(Qt.TextFormat.RichText)
        links.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        links.setOpenExternalLinks(True)
        layout.addWidget(links)
""",
    """        links.setTextFormat(Qt.TextFormat.RichText)
        links.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        links.setOpenExternalLinks(False)
        links.linkActivated.connect(lambda url: open_external_url(self, url))
        layout.addWidget(links)

        contact = QLabel(f"Contact: {CONTACT_EMAIL}")
        contact.setObjectName("contact")
        layout.addWidget(contact)
""",
    "GUI links/contact",
)

text = replace_once(
    text,
    "QLabel#outputs, QLabel#status, QLabel#links {",
    "QLabel#outputs, QLabel#status, QLabel#links, QLabel#contact {",
    "contact styling",
)

text = replace_once(
    text,
    """    print(f"{APP_NAME} {__version__}")
    print(f"Manual: {MANUAL_URL}")
""",
    """    print(f"{APP_NAME} {__version__}")
    print(f"Contact: {CONTACT_EMAIL}")
    print(f"Manual: {MANUAL_URL}")
""",
    "terminal contact",
)

path.write_text(text)

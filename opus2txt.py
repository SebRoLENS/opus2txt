#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "brukeropus",
#   "PySide6",
# ]
# ///

import io
import json
import math
import os
import subprocess
import sys
from pathlib import Path

try:
    from PySide6.QtCore import QSettings, Qt
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
        QDialog,
        QFileDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QSizePolicy,
        QSpacerItem,
        QVBoxLayout,
        QWidget,
    )
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency: PySide6\n"
        "Install the dependencies in your virtual environment with:\n"
        "  python -m pip install PySide6 brukeropus\n"
        "or run this script with:\n"
        "  pipx run ./opus2txt.py"
    ) from exc

try:
    from brukeropus import read_opus
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency: brukeropus\n"
        "Install the dependencies in your virtual environment with:\n"
        "  python -m pip install PySide6 brukeropus\n"
        "or run this script with:\n"
        "  pipx run ./opus2txt.py"
    ) from exc


__version__ = "1.1.0"

APP_NAME = "OPUS2TXT"
ORGANIZATION_NAME = "opus2txt"
MANUAL_URL = "https://github.com/SebRoLENS/opus2txt/blob/main/MANUAL.md"
GITHUB_URL = "https://github.com/SebRoLENS/opus2txt"
CONTACT_EMAIL = "romi@lens.unifi.it"


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
            "The link could not be opened automatically.\n\n"
            "If this does not work, copy this link into your browser:\n\n"
            f"{url}",
        )


def has_dot_hidden_component(path: str | Path) -> bool:
    """Return True if any real path component starts with '.'."""
    candidate = Path(path).expanduser()
    for part in candidate.parts:
        if part in {candidate.anchor, os.sep, ".", "..", ""}:
            continue
        if part.startswith("."):
            return True
    return False


def legacy_config_file() -> Path:
    """Return the configuration file used by the previous CustomTkinter version."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "opus2txt" / "config.json"


def load_legacy_last_directory() -> Path | None:
    """Read the old JSON preference once, if it exists."""
    try:
        with legacy_config_file().open("r", encoding="utf-8") as file:
            config = json.load(file)
        directory = Path(config.get("last_input_directory", "")).expanduser()
        if directory.is_dir() and not has_dot_hidden_component(directory):
            return directory
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError):
        pass
    return None


def valid_start_directory(path: str | Path | None) -> Path:
    """Return a safe existing start directory, falling back to Home."""
    if path:
        directory = Path(path).expanduser()
        if directory.is_dir() and not has_dot_hidden_component(directory):
            return directory
    return Path.home()


def has_numeric_extension(path: str | Path) -> bool:
    """Return True for filenames whose final extension is made only of digits."""
    suffix = Path(path).suffix
    return len(suffix) > 1 and suffix[1:].isdigit()


def process_opus_file(input_file: str, output_dir: str) -> None:
    """Extract absorbance, single-ray data and metadata from one OPUS file."""
    abs_dir = Path(output_dir) / "ABS"
    sray_dir = Path(output_dir) / "SRay"
    metadata_dir = Path(output_dir) / "METADATA"

    abs_dir.mkdir(parents=True, exist_ok=True)
    sray_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    opus_file = read_opus(input_file)
    base_name = Path(input_file).stem

    old_stdout = sys.stdout
    buffer = io.StringIO()
    try:
        sys.stdout = buffer
        opus_file.print_parameters()
    finally:
        sys.stdout = old_stdout

    metadata_filepath = metadata_dir / f"{base_name}_META.txt"
    metadata_filepath.write_text(buffer.getvalue(), encoding="utf-8")

    if "a" in opus_file.data_keys:
        output_file = abs_dir / f"{base_name}_ABS.txt"
        with output_file.open("w", encoding="utf-8") as file:
            file.write("wavenumber\tabsorbance\n")
            for x_value, y_value in zip(opus_file.a.x, opus_file.a.y):
                file.write(f"{x_value}\t{y_value}\n")

    if "sm" in opus_file.data_keys:
        output_file = sray_dir / f"{base_name}_SRay.txt"
        with output_file.open("w", encoding="utf-8") as file:
            file.write("wavenumber\ttransmittance\n")
            for x_value, y_value in zip(opus_file.sm.x, opus_file.sm.y):
                file.write(f"{x_value}\t{y_value}\n")


def process_opus_absorbance(sample_file: str, bg_file: str, output_dir: str) -> None:
    """Calculate absorbance from sample and background OPUS files and export datasets."""
    abs_dir = Path(output_dir) / "ABS"
    sray_dir = Path(output_dir) / "SRay"
    metadata_dir = Path(output_dir) / "METADATA"

    abs_dir.mkdir(parents=True, exist_ok=True)
    sray_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    sample_opus = read_opus(sample_file)
    bg_opus = read_opus(bg_file)

    base_name = Path(sample_file).stem

    # Export Metadata
    old_stdout = sys.stdout
    buffer = io.StringIO()
    try:
        sys.stdout = buffer
        sample_opus.print_parameters()
    finally:
        sys.stdout = old_stdout

    metadata_filepath = metadata_dir / f"{base_name}_META.txt"
    metadata_filepath.write_text(buffer.getvalue(), encoding="utf-8")

    # Export SRay for sample if available
    if "sm" in sample_opus.data_keys:
        output_file = sray_dir / f"{base_name}_SRay.txt"
        with output_file.open("w", encoding="utf-8") as file:
            file.write("wavenumber\ttransmittance\n")
            for x_value, y_value in zip(sample_opus.sm.x, sample_opus.sm.y):
                file.write(f"{x_value}\t{y_value}\n")

    # Compute Absorbance: A = -log10(S_sample / S_bg) = log10(S_bg / S_sample)
    if "sm" in sample_opus.data_keys and "sm" in bg_opus.data_keys:
        output_file = abs_dir / f"{base_name}_ABS.txt"
        with output_file.open("w", encoding="utf-8") as file:
            file.write("wavenumber\tabsorbance\n")
            for x_val, y_sample, y_bg in zip(
                sample_opus.sm.x, sample_opus.sm.y, bg_opus.sm.y
            ):
                if y_sample > 0 and y_bg > 0:
                    abs_val = math.log10(y_bg / y_sample)
                else:
                    abs_val = 0.0
                file.write(f"{x_val}\t{abs_val}\n")
    elif "a" in sample_opus.data_keys:
        # Fallback to pre-calculated absorbance if single-ray data is unavailable
        output_file = abs_dir / f"{base_name}_ABS.txt"
        with output_file.open("w", encoding="utf-8") as file:
            file.write("wavenumber\tabsorbance\n")
            for x_value, y_value in zip(sample_opus.a.x, sample_opus.a.y):
                file.write(f"{x_value}\t{y_value}\n")
    else:
        raise ValueError(f"Missing single-ray (sm) data in {Path(sample_file).name} or background file.")


class AbsorbanceDialog(QDialog):
    """Dialog window to handle background-subtracted Absorbance calculation."""

    def __init__(self, parent: "MainWindow"):
        super().__init__(parent)
        self.main_window = parent
        self.sample_paths: list[str] = []
        self.bg_path: str | None = None

        self.setWindowTitle("Calculate Absorbance")
        self.setMinimumSize(540, 360)
        self.resize(580, 380)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setObjectName("card")
        card.setFrameShape(QFrame.Shape.StyledPanel)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        title = QLabel("Calculate Absorbance")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        info = QLabel("Select OPUS sample spectra and a background OPUS file to compute absorbance.")
        info.setWordWrap(True)
        info.setObjectName("info")
        layout.addWidget(info)

        layout.addSpacing(6)

        # Sample Selection Row
        sample_row = QHBoxLayout()
        btn_samples = QPushButton("Select OPUS spectra")
        btn_samples.clicked.connect(self.select_samples)
        sample_row.addWidget(btn_samples)

        self.samples_label = QLabel("No sample files selected")
        self.samples_label.setObjectName("status")
        sample_row.addWidget(self.samples_label, stretch=1)
        layout.addLayout(sample_row)

        # Background Selection Row
        bg_row = QHBoxLayout()
        btn_bg = QPushButton("Select background file")
        btn_bg.clicked.connect(self.select_background)
        bg_row.addWidget(btn_bg)

        self.bg_label = QLabel("No background file selected")
        self.bg_label.setObjectName("status")
        bg_row.addWidget(self.bg_label, stretch=1)
        layout.addLayout(bg_row)

        layout.addSpacerItem(
            QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setFixedHeight(7)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status")
        layout.addWidget(self.status_label)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        btn_row.addStretch(1)

        self.calc_btn = QPushButton("Calculate")
        self.calc_btn.setObjectName("primaryButton")
        self.calc_btn.setDefault(True)
        self.calc_btn.clicked.connect(self.calculate)
        btn_row.addWidget(self.calc_btn)

        layout.addLayout(btn_row)

    def select_samples(self) -> None:
        files = self.main_window.choose_opus_files()
        if files:
            self.sample_paths = files
            self.samples_label.setText(f"{len(files)} sample file(s) selected")

    def select_background(self) -> None:
        start_dir = self.main_window.last_input_directory()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select background OPUS file",
            str(start_dir),
            "Bruker OPUS files (*.[0-9]*);;All files (*)",
        )
        if not file_path:
            return

        path = Path(file_path)
        if (
            has_dot_hidden_component(path)
            or not path.is_file()
            or not has_numeric_extension(path)
        ):
            QMessageBox.warning(
                self,
                "Invalid file",
                "The selected file is hidden or does not have a numeric extension.",
            )
            return

        self.bg_path = str(path)
        self.bg_label.setText(path.name)

    def calculate(self) -> None:
        if not self.sample_paths:
            QMessageBox.warning(self, "Missing samples", "Please select at least one sample OPUS file.")
            return

        if not self.bg_path:
            QMessageBox.warning(self, "Missing background", "Please select a background OPUS file.")
            return

        output_start_dir = Path(self.sample_paths[0]).parent
        output_dir = self.main_window.choose_output_directory(output_start_dir)
        if not output_dir:
            return

        self.calc_btn.setEnabled(False)
        self.progress.setRange(0, len(self.sample_paths))
        self.progress.setValue(0)

        completed = 0
        failed: list[str] = []

        try:
            for index, sample_file in enumerate(self.sample_paths, start=1):
                self.status_label.setText(f"Processing {Path(sample_file).name}…")
                QApplication.processEvents()

                try:
                    process_opus_absorbance(sample_file, self.bg_path, output_dir)
                except Exception as exc:
                    failed.append(Path(sample_file).name)
                    QMessageBox.critical(
                        self,
                        "Calculation error",
                        f"Could not process:\n{sample_file}\n\n{exc}",
                    )
                else:
                    completed += 1
                    self.main_window.save_last_input_directory(Path(sample_file).parent)

                self.progress.setValue(index)
                QApplication.processEvents()
        finally:
            self.calc_btn.setEnabled(True)

        if not failed:
            self.status_label.setText(f"Completed · {completed} file(s)")
            QMessageBox.information(
                self,
                "Completed",
                f"Absorbance calculation finished for {completed} file(s).",
            )
            self.accept()
        else:
            self.status_label.setText(
                f"Completed {completed} of {len(self.sample_paths)} file(s)"
            )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)
        self._migrate_legacy_setting_if_needed()

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(660, 410)
        self.resize(700, 440)
        self._build_ui()

    def _migrate_legacy_setting_if_needed(self) -> None:
        if self.settings.contains("last_input_directory"):
            return
        legacy = load_legacy_last_directory()
        if legacy is not None:
            self.settings.setValue("last_input_directory", str(legacy))

    def last_input_directory(self) -> Path:
        saved = self.settings.value("last_input_directory", "", type=str)
        return valid_start_directory(saved)

    def save_last_input_directory(self, directory: str | Path) -> None:
        directory = valid_start_directory(directory)
        self.settings.setValue("last_input_directory", str(directory))
        self.settings.sync()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(30, 30, 30, 30)

        card = QFrame()
        card.setObjectName("card")
        card.setFrameShape(QFrame.Shape.StyledPanel)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(34, 30, 34, 28)
        layout.setSpacing(12)

        title = QLabel(APP_NAME)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        subtitle = QLabel("Convert Bruker OPUS files to plain-text datasets.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        info = QLabel(
            "Select one or more OPUS files, then choose the output folder. New folders will be created"
        )
        info.setWordWrap(True)
        info.setObjectName("info")
        layout.addWidget(info)

        outputs = QLabel("Outputs in folders:  ABS (absorbance) ·  SRay (single ray) ·  METADATA")
        outputs.setObjectName("outputs")
        layout.addWidget(outputs)

        links = QLabel(
            f'<a href="{MANUAL_URL}">User manual</a>'
            ' &nbsp;·&nbsp; '
            f'<a href="{GITHUB_URL}">Check GitHub for updates and new releases</a>'
        )
        links.setObjectName("links")
        links.setTextFormat(Qt.TextFormat.RichText)
        links.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        links.setOpenExternalLinks(False)
        links.linkActivated.connect(lambda url: open_external_url(self, url))
        layout.addWidget(links)

        contact = QLabel(f"Contact: {CONTACT_EMAIL}")
        contact.setObjectName("contact")
        layout.addWidget(contact)

        layout.addSpacerItem(
            QSpacerItem(0, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setFixedHeight(7)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status")
        layout.addWidget(self.status_label)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        exit_button = QPushButton("Exit")
        exit_button.setObjectName("secondaryButton")
        exit_button.clicked.connect(self.close)
        button_row.addWidget(exit_button)

        button_row.addStretch(1)

        self.calc_abs_button = QPushButton("Calculate absorbance")
        self.calc_abs_button.setObjectName("secondaryButton")
        self.calc_abs_button.clicked.connect(self.open_absorbance_dialog)
        button_row.addWidget(self.calc_abs_button)

        self.convert_button = QPushButton("Select and convert")
        self.convert_button.setObjectName("primaryButton")
        self.convert_button.setDefault(True)
        self.convert_button.clicked.connect(self.select_and_convert)
        button_row.addWidget(self.convert_button)

        layout.addLayout(button_row)

        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: palette(window);
                color: palette(window-text);
            }
            QFrame#card {
                background: palette(base);
                border: 1px solid palette(midlight);
                border-radius: 16px;
            }
            QLabel#subtitle {
                color: palette(text);
                font-size: 14px;
            }
            QLabel#info {
                color: palette(text);
                font-size: 13px;
                margin-top: 6px;
            }
            QLabel#outputs, QLabel#status, QLabel#links, QLabel#contact {
                color: palette(text);
                font-size: 12px;
            }
            QPushButton {
                min-height: 36px;
                padding: 0 18px;
                border-radius: 8px;
            }
            QPushButton#primaryButton {
                font-weight: 600;
                padding: 0 24px;
            }
            QProgressBar {
                border: none;
                border-radius: 3px;
                background: palette(alternate-base);
            }
            QProgressBar::chunk {
                border-radius: 3px;
            }
            """
        )

    def open_absorbance_dialog(self) -> None:
        dialog = AbsorbanceDialog(self)
        dialog.exec()

    def choose_output_directory(self, start_dir: str | Path) -> str | None:
        start_dir = valid_start_directory(start_dir)

        selected = QFileDialog.getExistingDirectory(
            self,
            "Select output folder",
            str(start_dir),
            QFileDialog.Option.ShowDirsOnly,
        )

        if not selected:
            return None

        if has_dot_hidden_component(selected):
            QMessageBox.warning(
                self,
                "Hidden folder ignored",
                "Folders whose name starts with '.' cannot be used.",
            )
            return None

        return selected

    def choose_opus_files(self) -> list[str]:
        start_dir = self.last_input_directory()

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select OPUS files",
            str(start_dir),
            "Bruker OPUS files (*.[0-9]*);;All files (*)",
        )

        if not file_paths:
            return []

        accepted: list[str] = []
        ignored: list[str] = []

        for file_path in file_paths:
            path = Path(file_path)
            if (
                has_dot_hidden_component(path)
                or not path.is_file()
                or not has_numeric_extension(path)
            ):
                ignored.append(path.name)
                continue
            accepted.append(str(path))

        if ignored:
            preview = "\n".join(f"• {name}" for name in ignored[:8])
            if len(ignored) > 8:
                preview += f"\n• …and {len(ignored) - 8} more"
            QMessageBox.information(
                self,
                "Files ignored",
                "Hidden files or files without a numeric extension were ignored:\n\n"
                + preview,
            )

        return accepted

    def select_and_convert(self) -> None:
        self.status_label.setText("Selecting OPUS files…")
        QApplication.processEvents()
        file_paths = self.choose_opus_files()
        if not file_paths:
            self.status_label.setText("Ready")
            return

        self.status_label.setText("Selecting output folder…")
        QApplication.processEvents()
        output_start_dir = Path(file_paths[0]).parent
        output_dir = self.choose_output_directory(output_start_dir)
        if not output_dir:
            self.status_label.setText("Ready")
            return

        self.convert_button.setEnabled(False)
        self.progress.setRange(0, len(file_paths))
        self.progress.setValue(0)

        completed = 0
        failed: list[str] = []

        try:
            for index, file_path in enumerate(file_paths, start=1):
                self.status_label.setText(f"Processing {Path(file_path).name}…")
                QApplication.processEvents()

                try:
                    process_opus_file(file_path, output_dir)
                except Exception as exc:
                    failed.append(Path(file_path).name)
                    QMessageBox.critical(
                        self,
                        "Conversion error",
                        f"Could not process:\n{file_path}\n\n{exc}",
                    )
                else:
                    completed += 1
                    self.save_last_input_directory(Path(file_path).parent)

                self.progress.setValue(index)
                QApplication.processEvents()
        finally:
            self.convert_button.setEnabled(True)

        if not failed:
            self.status_label.setText(f"Completed · {completed} file(s)")
            QMessageBox.information(
                self,
                "Completed",
                "I've finished my work. So long, and thanks for all the fish.",
            )
        else:
            self.status_label.setText(
                f"Completed {completed} of {len(file_paths)} file(s)"
            )


def print_terminal_resources() -> None:
    """Show documentation and update links when launched from a terminal."""
    if getattr(sys, "stdout", None) is None:
        return
    print(f"{APP_NAME} {__version__}")
    print(f"Contact: {CONTACT_EMAIL}")
    print(f"Manual: {MANUAL_URL}")
    print(f"Check GitHub for updates and new releases: {GITHUB_URL}")
    print()


def main() -> int:
    print_terminal_resources()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setStyleSheet("")

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

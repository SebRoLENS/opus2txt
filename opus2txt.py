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
import os
import sys
from pathlib import Path

try:
    from PySide6.QtCore import QSettings, Qt
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
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


__version__ = "1.0.0"

APP_NAME = "OPUS2TXT"
ORGANIZATION_NAME = "opus2txt"
OPUS_EXTENSIONS = {".0", ".1", ".2", ".3", ".4"}


def has_dot_hidden_component(path: str | Path) -> bool:
    """Return True if any real path component starts with '.'."""
    candidate = Path(path).expanduser()
    for part in candidate.parts:
        # Ignore filesystem roots, drive anchors and navigation markers.
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)
        self._migrate_legacy_setting_if_needed()

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(620, 390)
        self.resize(680, 430)
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
            "Choose an output folder first, then select one or more OPUS files. "
            "The file chooser will open directly in the output folder."
        )
        info.setWordWrap(True)
        info.setObjectName("info")
        layout.addWidget(info)

        outputs = QLabel("Outputs:  ABS  ·  SRay  ·  METADATA")
        outputs.setObjectName("outputs")
        layout.addWidget(outputs)

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

        self.convert_button = QPushButton("Select and convert")
        self.convert_button.setObjectName("primaryButton")
        self.convert_button.setDefault(True)
        self.convert_button.clicked.connect(self.select_and_convert)
        button_row.addWidget(self.convert_button)

        layout.addLayout(button_row)

        # A restrained palette-aware stylesheet: Qt/system dialogs remain native.
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
                color: palette(mid);
                font-size: 14px;
            }
            QLabel#info {
                color: palette(text);
                font-size: 13px;
                margin-top: 6px;
            }
            QLabel#outputs, QLabel#status {
                color: palette(mid);
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

    def choose_output_directory(self) -> str | None:
        start_dir = self.last_input_directory()

        # QFileDialog uses the native platform dialog by default when available.
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

    def choose_opus_files(self, output_dir: str) -> list[str]:
        # IMPORTANT: this dialog starts exactly in the output directory just selected.
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select OPUS files",
            output_dir,
            "Bruker OPUS files (*.0 *.1 *.2 *.3 *.4);;All files (*)",
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
                or path.suffix.lower() not in OPUS_EXTENSIONS
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
                "Hidden or unsupported files were ignored:\n\n" + preview,
            )

        return accepted

    def select_and_convert(self) -> None:
        self.status_label.setText("Selecting output folder…")
        QApplication.processEvents()

        output_dir = self.choose_output_directory()
        if not output_dir:
            self.status_label.setText("Ready")
            return

        self.status_label.setText("Selecting OPUS files…")
        QApplication.processEvents()

        file_paths = self.choose_opus_files(output_dir)
        if not file_paths:
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
                    # Remember the location of the most recently processed file.
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


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setStyleSheet("")  # Keep the platform/desktop style as the base style.

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

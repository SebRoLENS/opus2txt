# opus2txt

[![Version](https://img.shields.io/github/v/release/SebRoLENS/opus2txt)](https://github.com/SebRoLENS/opus2txt/releases/latest)
[![DOI](https://img.shields.io/badge/DOI-pending-lightgrey)](https://github.com/SebRoLENS/opus2txt/releases/latest)

`opus2txt` is a graphical utility for extracting spectroscopy data from Bruker OPUS files into simple plain-text datasets and, when sample/background single-ray spectra are available, calculating absorbance spectra.

## Graphical interface

![opus2txt graphical interface](docs/opus2txt_gui.png)

The current PySide6/Qt interface provides two main workflows:

- **Select and convert** — extracts available absorbance, single-ray and metadata blocks from one or more OPUS files.
- **Calculate absorbance** — selects one or more sample OPUS files plus one background OPUS file and calculates absorbance from the single-ray spectra.

The GUI also provides a progress indicator, remembers the most recently used OPUS input directory, ignores hidden files/paths and files without numeric extensions, and includes direct links to the user manual and GitHub update page together with the author contact address.

## Download and run

For most users, the easiest way to use `opus2txt` is through the pre-built desktop application.

**No Python installation, terminal, PySide6, or separate `brukeropus` installation is required when using the packaged applications.**

**[Download the latest release](https://github.com/SebRoLENS/opus2txt/releases/latest)**

Looking for an older version? **[Browse all releases and previous versions](https://github.com/SebRoLENS/opus2txt/releases)**.

Available builds:

- **Linux x86_64:** AppImage
- **Windows x86_64:** standalone `.exe`
- **macOS Apple Silicon:** `.dmg`
- **macOS Intel x86_64:** `.dmg`

The Linux AppImage is cryptographically attested using open infrastructure. Windows and macOS builds remain unsigned because platform-trusted signing requires paid developer credentials, so they may display security warnings on first launch.

## What it does

`opus2txt` accepts Bruker OPUS files whose final extension is numeric, for example `.0`, `.1`, `.12` or `.123`.

### Extract existing OPUS data

For each selected file, the program can export:

- `ABS/<name>_ABS.txt` — absorbance spectrum, when an OPUS absorbance block (`a`) is present;
- `SRay/<name>_SRay.txt` — single-ray spectrum, when an OPUS single-ray block (`sm`) is present;
- `METADATA/<name>_META.txt` — parameters and metadata reported by `brukeropus`.

The `ABS`, `SRay`, and `METADATA` directories are created automatically inside the selected output directory.

### Calculate absorbance from sample and background

The **Calculate absorbance** workflow uses the sample and background single-ray spectra according to

```text
A = -log10(S_sample / S_background)
  =  log10(S_background / S_sample)
```

For every selected sample, the calculated absorbance is written to `ABS/<name>_ABS.txt`. The sample single-ray trace and metadata are also exported when available.

The sample and background should come from compatible measurements and should use the same spectral grid. If the required single-ray data are unavailable but the sample already contains an absorbance block, `opus2txt` falls back to exporting that existing absorbance spectrum. Otherwise it reports an error for that file and continues processing the remaining selected samples.

## Usage

### Convert existing OPUS traces

1. Launch the desktop application or `opus2txt.py`.
2. Press **Select and convert**.
3. Select one or more Bruker OPUS files.
4. Choose the output directory.
5. The program writes the available `ABS`, `SRay`, and `METADATA` text files and shows progress in the main window.

### Calculate absorbance

1. Press **Calculate absorbance**.
2. Select one or more sample OPUS spectra.
3. Select a single background OPUS file.
4. Press **Calculate** and choose the output directory.
5. The program calculates each absorbance spectrum, exports the associated data and reports progress in the dialog.

Files with non-numeric extensions, hidden files, and paths containing hidden components are ignored/rejected. The application remembers the most recently processed OPUS input directory between runs.

## Running from source

Running from source is optional and intended for users who want to inspect, modify, or develop the program.

Requirements:

- Python 3.10 or newer
- `PySide6`
- `brukeropus`

Using a virtual environment:

```bash
python3 -m venv ~/.venv/opus2txt
~/.venv/opus2txt/bin/python -m pip install PySide6 brukeropus
~/.venv/opus2txt/bin/python opus2txt.py
```

The script also contains PEP 723 dependency metadata, so recent versions of `pipx` can run it directly:

```bash
pipx run ./opus2txt.py
```

## Documentation

Detailed usage documentation is available in:

- [`MANUAL.md`](MANUAL.md)
- [PDF manual](MANUAL.pdf)

## Version

Current public version: **1.1.4**

## How to cite

If opus2txt contributes to published research, please acknowledge or cite the software. GitHub also provides a **Cite this repository** entry from [`CITATION.cff`](CITATION.cff).

Version **1.1.4** is archived automatically on Zenodo after the GitHub release is published. The DOI for this release is being assigned and will be inserted here automatically.

> Romi, S. (2026). *opus2txt* (Version 1.1.4) [Computer software]. GitHub. https://github.com/SebRoLENS/opus2txt/releases/tag/v1.1.4

Previous releases remain archived separately on Zenodo.

## License

This project is released under the MIT License. See [`LICENSE`](LICENSE).

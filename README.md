# opus2txt

[![Version](https://img.shields.io/github/v/release/SebRoLENS/opus2txt)](https://github.com/SebRoLENS/opus2txt/releases/latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21933187.svg)](https://doi.org/10.5281/zenodo.21933187)

`opus2txt` is a graphical utility for converting selected data from Bruker OPUS spectroscopy files into simple plain-text datasets.

## Download and run

For most users, the easiest way to use opus2txt is through the pre-built desktop application.

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

The program processes one or more Bruker OPUS files whose extension is numeric (`.0`, `.1`, `.2`, `.12`, `.123`, and so on) and creates, when the corresponding data are available:

- `ABS/<name>_ABS.txt` — absorbance spectrum with `wavenumber` and `absorbance` columns.
- `SRay/<name>_SRay.txt` — single-ray spectrum with `wavenumber` and `transmittance` columns.
- `METADATA/<name>_META.txt` — OPUS parameters and metadata reported by `brukeropus`.

The `ABS`, `SRay`, and `METADATA` directories are created automatically inside the selected output directory.

## Usage

1. Launch the desktop application or `opus2txt.py`.
2. Select one or more Bruker OPUS files.
3. Select the directory where the converted files should be written.
4. The program extracts the available absorbance, single-ray, and metadata blocks and writes the corresponding text files.

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

Current public version: **1.0.3**

## How to cite

If opus2txt contributes to published research, please acknowledge or cite the software. GitHub also provides a **Cite this repository** entry from [`CITATION.cff`](CITATION.cff).

> Romi, S. (2026). *opus2txt* (Version 1.0.3) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.21933187

DOI: [**10.5281/zenodo.21933187**](https://doi.org/10.5281/zenodo.21933187)

Previous releases remain archived separately on Zenodo.

## License

This project is released under the MIT License. See [`LICENSE`](LICENSE).

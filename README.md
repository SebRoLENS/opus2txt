# opus2txt

`opus2txt` is a graphical utility for converting selected data from Bruker OPUS spectroscopy files into plain-text files.

## What it does

The program processes one or more Bruker OPUS files (`.0` to `.4`) and creates, when the corresponding data are available:

- `ABS/<name>_ABS.txt` — absorbance spectrum with `wavenumber` and `absorbance` columns.
- `SRay/<name>_SRay.txt` — single-ray spectrum with `wavenumber` and `transmittance` columns.
- `METADATA/<name>_META.txt` — OPUS parameters and metadata reported by `brukeropus`.

The `ABS`, `SRay`, and `METADATA` directories are created automatically inside the selected output directory.

## Desktop applications

Pre-built desktop packages are available for users who do not want to install Python or use the command line:

- **Linux x86_64** — AppImage
- **Windows x86_64** — standalone `.exe`
- **macOS Apple Silicon** — `.dmg`
- **macOS Intel** — `.dmg`

Published application packages are distributed through the [GitHub Releases](https://github.com/SebRoLENS/opus2txt/releases) page.

The current desktop packages are not code-signed, so Windows SmartScreen or macOS Gatekeeper may display a security warning when opening them for the first time.

## Running from source

### Requirements

- Python 3.10 or newer
- `brukeropus`
- `PySide6`

### Virtual environment

```bash
python3 -m venv ~/.venv/opus2txt
~/.venv/opus2txt/bin/python -m pip install PySide6 brukeropus
```

Run with:

```bash
~/.venv/opus2txt/bin/python opus2txt.py
```

### pipx

The script contains PEP 723 dependency metadata, so recent versions of `pipx` can run it directly:

```bash
pipx run ./opus2txt.py
```

## Usage

1. Launch the desktop application or `opus2txt.py`.
2. Select the directory where the converted files should be written.
3. Select one or more Bruker OPUS files.
4. The program extracts the available absorbance, single-ray, and metadata blocks and writes the corresponding text files.

For a more detailed description of the workflow and output files, see [MANUAL.md](MANUAL.md).

## Citation

If you use **opus2txt** in scientific work, please cite:

**Romi, S. (2026). opus2txt (Version 1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.21921806**

A machine-readable citation file is provided in [`CITATION.cff`](CITATION.cff).

## License

This project is released under the MIT License. See [LICENSE](LICENSE).

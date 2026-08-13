# opus2txt

`opus2txt` is a cross-platform graphical utility for extracting data from Bruker OPUS spectroscopy files and exporting them as plain-text files.

## Features

- Native system file dialogs through PySide6/Qt on Linux, Windows and macOS.
- Batch selection of Bruker OPUS files (`.0` to `.4`).
- Exports absorbance spectra to `ABS/`.
- Exports single-ray/transmittance spectra to `SRay/`.
- Exports OPUS metadata to `METADATA/`.
- Remembers the directory of the most recently processed input file.
- Starts from the user's home directory on first launch.
- Rejects hidden files and paths containing components beginning with `.`.

## Requirements

- Python 3.10 or newer
- `brukeropus`
- `PySide6`

## Installation

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

## Quick usage

1. Launch `opus2txt.py`.
2. Choose the destination directory.
3. Select one or more OPUS files from the file dialog, which opens in the selected destination directory.
4. The application creates `ABS`, `SRay`, and `METADATA` subdirectories as needed.
5. A completion message is shown when conversion finishes.

For additional details, see [MANUAL.md](MANUAL.md).

## Citation

If you use **opus2txt** in scientific work, please cite the archived software release on **Zenodo**.

[Zenodo](https://zenodo.org/)

A machine-readable citation file is provided in [`CITATION.cff`](CITATION.cff). Once this repository is connected to Zenodo and the GitHub release is archived, the Zenodo DOI can be inserted here.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).

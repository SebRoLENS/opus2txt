# opus2txt

`opus2txt` is a graphical utility for converting selected data from Bruker OPUS spectroscopy files into plain-text files.

## What it does

The program processes one or more Bruker OPUS files (`.0` to `.4`) and creates, when the corresponding data are available:

- `ABS/<name>_ABS.txt` — absorbance spectrum with `wavenumber` and `absorbance` columns.
- `SRay/<name>_SRay.txt` — single-ray spectrum with `wavenumber` and `transmittance` columns.
- `METADATA/<name>_META.txt` — OPUS parameters and metadata reported by `brukeropus`.

The `ABS`, `SRay`, and `METADATA` directories are created automatically inside the selected output directory.

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

## Usage

1. Launch `opus2txt.py`.
2. Select the directory where the converted files should be written.
3. Select one or more Bruker OPUS files.
4. The program extracts the available absorbance, single-ray, and metadata blocks and writes the corresponding text files.

For a more detailed description of the workflow and output files, see [MANUAL.md](MANUAL.md).

## Citation

If you use **opus2txt** in scientific work, please cite the archived software release on Zenodo:

**Sebastiano Romi. opus2txt, version 1.0.0. Zenodo. https://doi.org/10.5281/zenodo.21921806**

[DOI: 10.5281/zenodo.21921806](https://doi.org/10.5281/zenodo.21921806)

A machine-readable citation file is provided in [`CITATION.cff`](CITATION.cff).

## License

This project is released under the MIT License. See [LICENSE](LICENSE).

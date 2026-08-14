# opus2txt User Manual

**Current manual version: 1.0.2**

**Author:** Sebastiano Romi  
**Affiliation:** European Laboratory for non-Linear Spectroscopy (LENS), Università degli Studi di Firenze (UNIFI)  
**Contact:** [romi@lens.unifi.it](mailto:romi@lens.unifi.it)

## Purpose

`opus2txt` converts selected data blocks from Bruker OPUS spectroscopy files into simple tab-separated text files suitable for plotting, fitting, spreadsheet, or scientific-analysis software.

This manual is available both as [`MANUAL.md`](MANUAL.md) and as [`MANUAL.pdf`](MANUAL.pdf). The PDF copy is regenerated automatically whenever the Markdown manual is updated. During an automatic software release, both manual files are versioned together with the application.

## Download and start the application

Pre-built desktop applications are available from the [latest GitHub Release](https://github.com/SebRoLENS/opus2txt/releases/latest). These packages include the required runtime and dependencies, so Python, PySide6, and `brukeropus` do not need to be installed separately.

Available packages:

- **[Linux x86_64 — AppImage](https://github.com/SebRoLENS/opus2txt/releases/latest)**
- **[Windows x86_64 — standalone `.exe`](https://github.com/SebRoLENS/opus2txt/releases/latest)**
- **[macOS Apple Silicon — `.dmg`](https://github.com/SebRoLENS/opus2txt/releases/latest)**
- **[macOS Intel — `.dmg`](https://github.com/SebRoLENS/opus2txt/releases/latest)**

Older versions remain available from the [complete GitHub Releases archive](https://github.com/SebRoLENS/opus2txt/releases).

### Linux

Download the AppImage corresponding to the current release. If required by the desktop environment, mark the file as executable in its file properties, then open it normally.

The Linux AppImage is cryptographically attested through the project's GitHub Actions build process.

### Windows

Download the `.exe` file and open it normally. No installation is required.

The Windows build is currently unsigned, so Windows may display a security warning when the application is opened for the first time.

### macOS

Download the `.dmg` matching the Mac architecture:

- `arm64` for Apple Silicon Macs.
- `x86_64` for Intel Macs.

Open the DMG and launch `opus2txt`. The macOS builds are currently unsigned, so macOS may display a security warning when the application is opened for the first time.

## Workflow

### 1. Select OPUS files

Press **Select and convert**. The application immediately opens the system file-selection dialog.

Select one or more Bruker OPUS files. `opus2txt` accepts files whose extension consists entirely of digits, for example:

```text
sample.0
sample.1
sample.4
sample.12
sample.123
```

Files with non-numeric extensions are ignored. Hidden files and paths containing hidden components (names beginning with `.`) are rejected.

On first launch the file dialog starts from the user's home directory. After successful conversions, `opus2txt` remembers the location of the most recently processed OPUS input file for future launches.

### 2. Select the output folder

After the OPUS files have been selected, the application opens the output-folder dialog.

The dialog starts from the directory containing the first selected input file. Choose the directory where the converted files should be written.

### 3. Generated files

For each selected OPUS file, `opus2txt` creates up to three output types.

#### ABS

If the OPUS file contains an absorbance block (`a`), data are written to:

```text
ABS/<original_name>_ABS.txt
```

with columns:

```text
wavenumber    absorbance
```

#### SRay

If the OPUS file contains a single-ray block (`sm`), data are written to:

```text
SRay/<original_name>_SRay.txt
```

with columns:

```text
wavenumber    transmittance
```

#### METADATA

Parameters printed by `brukeropus` are written to:

```text
METADATA/<original_name>_META.txt
```

## Existing output directories

The `ABS`, `SRay`, and `METADATA` directories are created automatically when needed. Existing directories are reused.

## Errors

If an OPUS file cannot be read or converted, the application displays an error message identifying the file. Other selected files continue to be processed.

## Running from source

Running from source is optional and intended for users who want to inspect, modify, or develop the program.

### Dependencies

```text
Python >= 3.10
PySide6
brukeropus
```

### Virtual environment

Using a dedicated virtual environment:

```bash
python3 -m venv ~/.venv/opus2txt
~/.venv/opus2txt/bin/python -m pip install PySide6 brukeropus
~/.venv/opus2txt/bin/python opus2txt.py
```

### pipx

With a recent version of `pipx`:

```bash
pipx run ./opus2txt.py
```

## Platform support

The graphical interface uses PySide6/Qt. Qt requests the native platform file dialog when available, allowing integration with Linux desktop environments and the normal system dialogs on Windows and macOS.

## Citation

For scientific use, please cite the archived Zenodo release corresponding to the version used. See the Citation section of the README and `CITATION.cff`.

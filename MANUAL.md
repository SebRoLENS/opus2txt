# opus2txt User Manual

## Purpose

`opus2txt` converts selected data blocks from Bruker OPUS spectroscopy files into simple tab-separated text files suitable for plotting, fitting, spreadsheet, or scientific-analysis software.

## Starting the application

Using a dedicated virtual environment:

```bash
~/.venv/opus2txt/bin/python opus2txt.py
```

Or with a recent version of `pipx`:

```bash
pipx run ./opus2txt.py
```

## Workflow

### 1. Select the output folder

Press **Select and convert**. The first dialog asks for the output directory. On first launch the dialog starts from the user's home directory. After successful conversions, opus2txt remembers the location of the most recently processed OPUS input file for future launches.

Paths containing hidden components (names beginning with `.`) are rejected.

### 2. Select OPUS files

After choosing the output directory, a second file dialog opens starting from that directory. Select one or more Bruker OPUS files with extensions `.0`, `.1`, `.2`, `.3`, or `.4`.

Hidden files and unsupported extensions are ignored.

### 3. Generated files

For each selected OPUS file, opus2txt creates up to three output types.

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

## Platform support

The graphical interface uses PySide6/Qt. Qt requests the native platform file dialog when available, allowing integration with Linux desktop environments and the normal system dialogs on Windows and macOS.

## Dependencies

```text
Python >= 3.10
PySide6
brukeropus
```

## Citation

For scientific use, please cite the archived Zenodo release corresponding to the version used. See the Citation section of the README and `CITATION.cff`.

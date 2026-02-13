# Building PyMacroRecord

This guide explains how to rebuild the application executable and Windows installer after making code changes.

## Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Inno Setup 6** (for the installer) — download from https://jrsoftware.org/isdl.php

Install Python dependencies and PyInstaller:

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Version Bump (if releasing a new version)

Update the version string in **both** of these files:

1. `src/utils/version.py` — change `self.version = "x.y.z"`
2. `installer.iss` — change `#define MyAppVersion "x.y.z"`

## Step 1: Build the Executable

From the project root, run:

```bash
python -m PyInstaller --noconfirm --onedir --windowed ^
    --icon "src/assets/logo.ico" ^
    --name "PyMacroRecord" ^
    --contents-directory "." ^
    --add-data "src/assets;assets/" ^
    --add-data "src/hotkeys;hotkeys/" ^
    --add-data "src/macro;macro/" ^
    --add-data "src/utils;utils/" ^
    --add-data "src/windows;windows/" ^
    --add-data "src/langs;langs" ^
    "src/main.py"
```

Or, if the `PyMacroRecord.spec` file already exists, simply run:

```bash
python -m PyInstaller --noconfirm PyMacroRecord.spec
```

This produces the bundled application in `dist/PyMacroRecord/`.

You can verify the build by running `dist/PyMacroRecord/PyMacroRecord.exe` directly.

## Step 2: Build the Installer

Make sure Step 1 is complete (the `dist/PyMacroRecord/` folder must exist).

Run the Inno Setup compiler:

```bash
iscc installer.iss
```

> If `iscc` is not in your PATH, use the full path to the compiler, for example:
> ```bash
> "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
> ```

The installer will be created at:

```
installer_output/PyMacroRecord-<version>-Setup.exe
```

## Project Structure (build-related files)

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `PyMacroRecord.spec` | PyInstaller build configuration (auto-generated) |
| `installer.iss` | Inno Setup installer script |
| `src/utils/version.py` | Application version string |
| `src/assets/logo.ico` | Application icon |
| `LICENSE.md` | License file (shown during installation) |
| `dist/` | PyInstaller output (not committed) |
| `build/` | PyInstaller temp files (not committed) |
| `installer_output/` | Installer output (not committed) |

## Quick Rebuild (both steps)

```bash
python -m PyInstaller --noconfirm PyMacroRecord.spec && iscc installer.iss
```

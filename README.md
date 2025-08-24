# Updated_FileComp - macOS App Builder

This project provides an automated workflow to build a macOS application from a Python script (`Updated_FileComp.py`) and package it as a DMG file using GitHub Actions. The workflow includes creating a standalone `.app` and generating a distributable `.dmg` for easy installation.

---

## Features

- Automatically builds a standalone macOS application using **PyInstaller**.
- Packages the app into a `.dmg` file using `hdiutil`.
- Supports a custom app icon (`iconformac.icns`).
- Fully automated on GitHub Actions upon pushing to the `main` branch.

---

## Requirements

- Python 3.11
- GitHub repository with the following files:
  - `Updated_FileComp.py` (main Python script)
  - `iconformac.icns` (app icon)
- macOS runner (GitHub Actions uses `macos-latest`)

---

## Usage

### GitHub Actions Workflow

The workflow automatically executes the following steps:

1. **Checkout repository**
2. **Set up Python 3.11**
3. **Install dependencies**
   ```bash
   python -m pip install --upgrade pip
   pip install pyinstaller


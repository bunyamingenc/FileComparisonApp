Live File Comparison — Qt

A desktop application for real-time, character-level text comparison. It highlights differences between two files (source vs. target) and supports dark/light themes, easy file loading, and saving changes. Built with Python 3 and PySide6 (Qt for Python).


Features

Compare two text files side by side.

Character-level diff highlighting:

Red = removed/mismatched in source

Green = added/mismatched in target

Gray = unchanged

Dark/Light theme toggle.

Load and save files directly from the toolbar.

Clear all content with a single click.

Automatic live comparison as you type.

Installation
Requirements

Python 3.10+

PySide6

pip install PySide6

Run from source
git clone https://github.com/USERNAME/live-file-comparison.git
cd live-file-comparison
python main.py

Building Executables

This project provides cross-platform builds via GitHub Actions.

# Live File Comparison — Qt

A desktop application for real-time, character-level text comparison. It highlights differences between two files (source vs. target) and supports dark/light themes, easy file loading, and saving changes.

---

## Features

- **Compare two text files side by side**
- **Character-level diff highlighting:**
  - **Red**: Removed or mismatched in source
  - **Green**: Added or mismatched in target
  - **Gray**: Unchanged
- **Dark/Light theme toggle**
- **Load and save files directly from the toolbar**
- **Clear all content with a single click**
- **Automatic live comparison as you type**

---

## Installation

### Requirements

- Python **3.10+**
- [PySide6](https://pypi.org/project/PySide6/)

Install dependencies:

```bash
pip install PySide6
```

---

## Run from Source

```bash
git clone https://github.com/bunyamingenc/FileComparisonApp.git
cd FileComparisonApp
python main.py
```

---

## Building Executables

Cross-platform builds are provided via GitHub Actions.

---

## License

[MIT](LICENSE)


---

## Contributing

Contributions are welcome! Please open issues or pull requests for improvements, bug fixes, or new features.

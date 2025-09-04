import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QFont, QTextCharFormat, QTextCursor, QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
    QPlainTextEdit,
    QTextEdit,
    QSplitter,
    QToolBar,
    QLabel,
    QSizePolicy,
)
import difflib

# =============================
# Diff utilities
# =============================
ColorSpan = Tuple[str, str]  # (tag, text)

def highlight_diff(line1: str, line2: str) -> Tuple[List[ColorSpan], List[ColorSpan]]:
    """Karakter bazlı diff: aynı pozisyonda olmayan her harf kırmızı/yeşil olur."""
    res1: List[ColorSpan] = []
    res2: List[ColorSpan] = []

    max_len = max(len(line1), len(line2))

    for i in range(max_len):
        c1 = line1[i] if i < len(line1) else ""
        c2 = line2[i] if i < len(line2) else ""

        if c1 == c2 and c1 != "":
            res1.append(("eq", c1))
            res2.append(("eq", c2))
        else:
            if c1:
                res1.append(("red", c1))
            if c2:
                res2.append(("green", c2))

    return res1, res2


# =============================
# Theming
# =============================
@dataclass
class Theme:
    name: str
    bg_main: str        # Ana arka plan (window)
    bg_text: str        # Panel arka planı (text edit)
    fg_text: str
    line_color: str
    accent: str
    diff_equal: str
    toolbar_btn_color: str

# Light mod artık koyu gri arka plan, açık gri paneller
LIGHT = Theme(
    name="light",
    bg_main="#2e2e2e",       # Ana arka plan: koyu gri, göz yormayan
    bg_text="#d6d6d6",       # Paneller: açık gri
    fg_text="#111111",        # Yazılar: koyu renk
    line_color="#3566e0",     # Başlıklar, line headers
    accent="#3566e0",
    diff_equal="#444444",
    toolbar_btn_color="#111111",  # Toolbar butonları koyu renk
)


DARK = Theme(
    name="dark",
    bg_main="#0d1b2a",
    bg_text="#2b2b2b",
    fg_text="#eaeff5",
    line_color="#66e0ff",
    accent="#78a1ff",
    diff_equal="#b9c2cd",
    toolbar_btn_color="#78a1ff",
)


# =============================
# Main Window
# =============================
class DiffWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live File Comparison — Qt")
        self.resize(1200, 800)

        self._apply_high_dpi()

        self.theme: Theme = DARK
        self.file1_path: Optional[str] = None
        self.file2_path: Optional[str] = None
        self._compare_timer = QTimer(self)
        self._compare_timer.setInterval(200)
        self._compare_timer.setSingleShot(True)
        self._compare_timer.timeout.connect(self.compare_texts)

        self.mono = QFont("Courier New") if sys.platform.startswith("win") else QFont("Menlo")
        self.mono.setStyleHint(QFont.Monospace)
        self.mono.setPointSize(11)

        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        # Toolbar
        self.toolbar = QToolBar("Main")
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self._build_toolbar()

        # Split editors
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Left panel
        left_panel = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_panel)

        self.lbl_source = QLabel("Source")
        f = QFont()
        f.setPointSize(12)
        f.setBold(True)
        self.lbl_source.setFont(f)
        self.lbl_source.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.text1 = QPlainTextEdit()
        self.text1.setWordWrapMode(self.text1.wordWrapMode())
        self.text1.setFont(self.mono)

        left_panel.addWidget(self.lbl_source)
        left_panel.addWidget(self.text1, 1)

        # Right panel
        right_panel = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        self.lbl_target = QLabel("Target")
        f2 = QFont()
        f2.setPointSize(12)
        f2.setBold(True)
        self.lbl_target.setFont(f2)
        self.lbl_target.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.text2 = QPlainTextEdit()
        self.text2.setWordWrapMode(self.text2.wordWrapMode())
        self.text2.setFont(self.mono)

        right_panel.addWidget(self.lbl_target)
        right_panel.addWidget(self.text2, 1)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([1, 1])
        v.addWidget(splitter, 1)

        # Diff box
        self.diff_box = QTextEdit()
        self.diff_box.setReadOnly(True)
        self.diff_box.setFont(self.mono)
        self.diff_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        v.addWidget(self.diff_box, 1)

        self.text1.textChanged.connect(self._schedule_compare)
        self.text2.textChanged.connect(self._schedule_compare)

        self.apply_theme(self.theme)

    # ---------- Toolbar
    def _build_toolbar(self):
        act_load = QAction("Load Files", self)
        act_load.triggered.connect(self.load_files)

        act_save = QAction("Save Changes", self)
        act_save.triggered.connect(self.save_files)

        self.act_theme = QAction("Light Mode", self)
        self.act_theme.triggered.connect(self.toggle_theme)

        act_clear = QAction("Clear", self)
        act_clear.triggered.connect(self.clear_all)

        self.toolbar.addAction(act_load)
        self.toolbar.addAction(act_save)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_theme)
        self.toolbar.addSeparator()
        self.toolbar.addAction(act_clear)

    # ---------- High DPI helpers
    def _apply_high_dpi(self):
        try:
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
        except Exception:
            pass

    # ---------- Theming
    def apply_theme(self, theme: Theme):
        self.theme = theme
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(theme.bg_main))
        pal.setColor(QPalette.ColorRole.Base, QColor(theme.bg_text))
        pal.setColor(QPalette.ColorRole.Text, QColor(theme.fg_text))
        pal.setColor(QPalette.ColorRole.WindowText, QColor(theme.fg_text))
        self.setPalette(pal)

        css = (
    f"QPlainTextEdit, QTextEdit {{ background: {theme.bg_text}; color: {theme.fg_text}; "
    f"border: 1px solid rgba(0,0,0,0.08); border-radius: 10px; padding: 8px; }} "
    f"QToolBar {{ background: {theme.bg_main}; border: none; }} "
    f"QToolButton {{ color: {theme.toolbar_btn_color}; }} "
    f"QLabel {{ color: {theme.line_color}; }}"
)

        self.setStyleSheet(css)

        self.act_theme.setText("Light Mode" if theme is DARK else "Dark Mode")
        self.compare_texts()

    def toggle_theme(self):
        self.apply_theme(DARK if self.theme is LIGHT else LIGHT)

    # ---------- File ops
    def load_files(self):
        path1, _ = QFileDialog.getOpenFileName(self, "Select Source File", "", "Text Files (*.txt *.json *.yml *.yaml *.csv *.tsv *.md);;All Files (*)")
        if not path1:
            return
        path2, _ = QFileDialog.getOpenFileName(self, "Select Target File", "", "Text Files (*.txt *.json *.yml *.yaml *.csv *.tsv *.md);;All Files (*)")
        if not path2:
            return
        try:
            with open(path1, "r", encoding="utf-8") as f:
                content1 = f.read()
            with open(path2, "r", encoding="utf-8") as f:
                content2 = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read files:\n{e}")
            return

        self.file1_path = path1
        self.file2_path = path2
        self.text1.blockSignals(True)
        self.text2.blockSignals(True)
        self.text1.setPlainText(content1)
        self.text2.setPlainText(content2)
        self.text1.blockSignals(False)
        self.text2.blockSignals(False)
        self.compare_texts()

    def save_files(self):
        if not self.file1_path or not self.file2_path:
            QMessageBox.warning(self, "Warning", "You need to load files first!")
            return
        try:
            content1 = self.text1.toPlainText().rstrip("\n")
            content2 = self.text2.toPlainText().rstrip("\n")
            with open(self.file1_path, "w", encoding="utf-8") as f:
                f.write(content1)
            with open(self.file2_path, "w", encoding="utf-8") as f:
                f.write(content2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save files:\n{e}")
            return
        QMessageBox.information(self, "Saved", "Files have been updated and saved successfully!")

    def clear_all(self):
        self.text1.clear()
        self.text2.clear()
        self.file1_path = None
        self.file2_path = None
        self.diff_box.clear()

    # ---------- Compare
    def _schedule_compare(self):
        self._compare_timer.start()

    def compare_texts(self):
        f1_lines = self.text1.toPlainText().splitlines()
        f2_lines = self.text2.toPlainText().splitlines()
        max_lines = max(len(f1_lines), len(f2_lines))
        differences_found = False

        self.diff_box.clear()
        cursor = self.diff_box.textCursor()

        for i in range(max_lines):
            l1 = f1_lines[i] if i < len(f1_lines) else ""
            l2 = f2_lines[i] if i < len(f2_lines) else ""

            if l1 != l2:
                differences_found = True
                res1, res2 = highlight_diff(l1, l2)

                self._append_line_header(cursor, f"Line {i+1} (Source): ")
                self._append_spans(cursor, res1)
                self._append_newline(cursor)

                self._append_line_header(cursor, f"Line {i+1} (Target): ")
                self._append_spans(cursor, res2)
                self._append_newline(cursor)
                self._append_newline(cursor)

        if not differences_found:
            self._append_identical(cursor, "No differences detected – the texts are identical.")

        self.diff_box.moveCursor(QTextCursor.Start)

    # ---------- Rich text helpers
    def _format(self, color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def _append(self, cursor: QTextCursor, text: str, fmt: Optional[QTextCharFormat] = None):
        if fmt:
            cursor.mergeCharFormat(fmt)
        cursor.insertText(text)

    def _append_newline(self, cursor: QTextCursor):
        cursor.insertBlock()

    def _append_line_header(self, cursor: QTextCursor, text: str):
        self._append(cursor, text, self._format(self.theme.line_color, bold=True))

    def _append_identical(self, cursor: QTextCursor, text: str):
        self._append(cursor, text, self._format(self.theme.diff_equal, italic=True))

    def _append_spans(self, cursor: QTextCursor, spans: List[ColorSpan]):
        for tag, content in spans:
            if not content:
                continue
            if tag == "red":
                self._append(cursor, content, self._format("#ff4d4f", bold=True))
            elif tag == "green":
                self._append(cursor, content, self._format("#3cb371", bold=True))
            else:
                self._append(cursor, content, self._format(self.theme.diff_equal))

# =============================
# Entrypoint
# =============================
def main():
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    win = DiffWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

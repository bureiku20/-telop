from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from .analysis import infer_style_from_images
from .jsx_builder import build_jsx
from .ae_runner import run_after_effects
from .models import TelopStyle
from .preview import TelopPreview

RESOURCE_DIR = Path(__file__).resolve().parent / "resources"
DIST_DIR = Path(__file__).resolve().parent / "dist"
DIST_DIR.mkdir(exist_ok=True)


class DisclaimerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Disclaimer")
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.hasScrolled = False

        text = (RESOURCE_DIR / "disclaimer.txt").read_text(encoding="utf-8")
        self.text_hash = hashlib.sha1(text.encode("utf-8")).hexdigest()[:6]

        self.editor = QPlainTextEdit(readOnly=True)
        self.editor.setPlainText(text)
        self.editor.verticalScrollBar().valueChanged.connect(self._on_scroll)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress_label = QLabel("Read 0% • Scroll to the end to continue")

        self.checkbox = QCheckBox("I Understand / 内容を理解しました")
        self.checkbox.stateChanged.connect(self._update_button)

        self.continue_btn = QPushButton("Continue / 続行")
        self.continue_btn.setEnabled(False)
        self.continue_btn.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Disclaimer Rev: {self.text_hash}"))
        layout.addWidget(self.editor)
        layout.addWidget(self.progress)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.continue_btn)

    def _on_scroll(self, value: int) -> None:
        sb = self.editor.verticalScrollBar()
        maximum = sb.maximum()
        percent = int(value / maximum * 100) if maximum > 0 else 100
        self.progress.setValue(percent)
        if value >= maximum - 2:
            self.hasScrolled = True
            self.progress_label.setText("Read 100% • Scroll complete")
        else:
            self.progress_label.setText(f"Read {percent}% • Scroll to the end to continue")
        self._update_button()

    def _update_button(self) -> None:
        self.continue_btn.setEnabled(self.hasScrolled and self.checkbox.isChecked())

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        event.ignore()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() in (Qt.Key_Escape, Qt.Key_W) and (
            event.modifiers() & (Qt.ControlModifier | Qt.MetaModifier | Qt.AltModifier)
        ):
            event.ignore()
        elif event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telop From Image")

        self.style: TelopStyle | None = None

        self.preview = TelopPreview()
        self.editor = QPlainTextEdit()

        open_btn = QPushButton("Open Image")
        open_btn.clicked.connect(self.open_image)

        update_btn = QPushButton("Update Preview")
        update_btn.clicked.connect(self.update_preview_from_editor)

        save_btn = QPushButton("Save Style")
        save_btn.clicked.connect(self.save_style)

        load_btn = QPushButton("Load Style")
        load_btn.clicked.connect(self.load_style)

        jsx_btn = QPushButton("Generate JSX")
        jsx_btn.clicked.connect(self.generate_jsx)

        ae_btn = QPushButton("Run in AE & Export")
        ae_btn.clicked.connect(self.run_ae)

        layout = QVBoxLayout()
        layout.addWidget(self.preview)
        layout.addWidget(self.editor)

        btn_layout = QHBoxLayout()
        for b in [open_btn, update_btn, save_btn, load_btn, jsx_btn, ae_btn]:
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # GUI actions
    def open_image(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Image", str(Path.home()))
        if not paths:
            return
        try:
            self.style = infer_style_from_images(paths)
            self.editor.setPlainText(self.style.to_json())
            self.preview.update_style(self.style)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Error", str(e))

    def update_preview_from_editor(self):
        try:
            data = self.editor.toPlainText()
            self.style = TelopStyle.from_json(data)
            self.preview.update_style(self.style)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Error", str(e))

    def save_style(self):
        if self.style is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Style", str(Path.home()), "JSON Files (*.json)")
        if path:
            Path(path).write_text(self.style.to_json(), encoding="utf-8")

    def load_style(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Style", str(Path.home()), "JSON Files (*.json)")
        if not path:
            return
        data = Path(path).read_text(encoding="utf-8")
        self.style = TelopStyle.from_json(data)
        self.editor.setPlainText(self.style.to_json())
        self.preview.update_style(self.style)

    def generate_jsx(self):
        if self.style is None:
            return
        jsx_path = DIST_DIR / (self.style.template_name + ".jsx")
        mogrt_path = DIST_DIR / (self.style.template_name + ".mogrt")
        build_jsx(self.style, jsx_path, mogrt_path)
        QMessageBox.information(self, "JSX Generated", str(jsx_path))

    def run_ae(self):
        if self.style is None:
            return
        jsx_path = DIST_DIR / (self.style.template_name + ".jsx")
        mogrt_path = DIST_DIR / (self.style.template_name + ".mogrt")
        build_jsx(self.style, jsx_path, mogrt_path)
        try:
            proc = run_after_effects(jsx_path, mogrt_path)
            QMessageBox.information(self, "AE Output", proc.stdout + "\n" + proc.stderr)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Error", str(e))


def main() -> None:
    app = QApplication([])
    d = DisclaimerDialog()
    d.exec()
    w = MainWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    main()

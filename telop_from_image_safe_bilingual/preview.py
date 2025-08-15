from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel

from .models import TelopStyle


class TelopPreview(QLabel):
    """Simple preview widget rendering the telop using QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 200)
        self.setAlignment(Qt.AlignCenter)
        self._style = None

    def update_style(self, style: TelopStyle) -> None:
        self._style = style
        comp = style.comp
        img = QImage(comp["width"], comp["height"], QImage.Format_ARGB32)
        img.fill(Qt.transparent)

        painter = QPainter(img)
        font = QFont(style.font_name, style.font_size)
        font.setLetterSpacing(QFont.AbsoluteSpacing, style.tracking)
        painter.setFont(font)
        text = style.text or ""

        # draw strokes from inner to outer
        for stroke in reversed(style.strokes):
            pen = QPen(QColor.fromRgbF(*stroke["color"]), stroke["width"], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawText(style.position["x"], style.position["y"], text)

        # fill
        pen = QPen(QColor.fromRgbF(*style.fill["color"]))
        painter.setPen(pen)
        painter.drawText(style.position["x"], style.position["y"], text)
        painter.end()

        pix = QPixmap.fromImage(img)
        self.setPixmap(pix.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

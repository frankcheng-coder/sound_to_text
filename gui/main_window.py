"""
Main application window.

Responsibilities:
  - Drag-and-drop zone for .m4a files
  - File path display
  - Transcribe button
  - Progress bar + status label
  - Launches TranscriptionWorker on a background QThread
"""

from __future__ import annotations

import os
import traceback

from PySide6.QtCore import (
    QThread,
    QObject,
    Signal,
    Qt,
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPalette, QColor
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from transcription.transcriber import transcribe


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

class TranscriptionWorker(QObject):
    """Runs transcription in a background thread and emits progress signals."""

    progress = Signal(int, str)    # (percent, message)
    finished = Signal(str, str)    # (txt_path, srt_path)
    error = Signal(str)            # error message

    def __init__(self, audio_path: str, language: str | None) -> None:
        super().__init__()
        self._audio_path = audio_path
        self._language = language

    def run(self) -> None:
        try:
            txt_path, srt_path = transcribe(
                self._audio_path,
                language=self._language,
                progress_callback=lambda pct, msg: self.progress.emit(pct, msg),
            )
            self.finished.emit(txt_path, srt_path)
        except Exception as exc:
            self.error.emit(f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()}")


# ---------------------------------------------------------------------------
# Drop zone widget
# ---------------------------------------------------------------------------

class DropZone(QWidget):
    """A rectangular widget that accepts .m4a drag-and-drop."""

    file_dropped = Signal(str)   # emits the dropped file path

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet(
            """
            DropZone {
                border: 2px dashed #888;
                border-radius: 10px;
                background-color: #1e1e1e;
            }
            DropZone:hover {
                border-color: #5ea6f5;
                background-color: #232d3b;
            }
            """
        )
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("🎵")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(28)
        icon_label.setFont(icon_font)

        hint_label = QLabel("Drop an .m4a file here\nor click to browse")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #aaa; font-size: 13px;")

        layout.addWidget(icon_label)
        layout.addWidget(hint_label)

    # ------------------------------------------------------------------
    # Drag-and-drop handlers
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        file_path = urls[0].toLocalFile()
        self.file_dropped.emit(file_path)

    def mousePressEvent(self, _event) -> None:  # noqa: ANN001
        """Open file dialog on click."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select .m4a file", os.path.expanduser("~"), "Audio Files (*.m4a)"
        )
        if path:
            self.file_dropped.emit(path)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """Application main window."""

    # Maps display label -> ISO-639-1 code (None = auto-detect)
    LANGUAGES: list[tuple[str, str | None]] = [
        ("Auto-detect", None),
        ("English", "en"),
        ("Chinese (Simplified)", "zh"),
        ("Japanese", "ja"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sound to Text")
        self.setMinimumSize(520, 420)
        self._audio_path: str | None = None
        self._thread: QThread | None = None
        self._worker: TranscriptionWorker | None = None
        self._setup_ui()
        self._apply_dark_palette()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # Title
        title = QLabel("Sound to Text")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        # Drop zone
        self._drop_zone = DropZone()
        self._drop_zone.file_dropped.connect(self._on_file_selected)
        root.addWidget(self._drop_zone)

        # File path row
        path_row = QHBoxLayout()
        path_label = QLabel("File:")
        path_label.setFixedWidth(36)
        self._path_display = QLabel("No file selected")
        self._path_display.setStyleSheet("color: #888; font-size: 12px;")
        self._path_display.setWordWrap(True)
        path_row.addWidget(path_label)
        path_row.addWidget(self._path_display)
        root.addLayout(path_row)

        # Language selector row
        lang_row = QHBoxLayout()
        lang_label = QLabel("Language:")
        lang_label.setFixedWidth(70)
        self._lang_combo = QComboBox()
        self._lang_combo.setFixedHeight(30)
        self._lang_combo.setStyleSheet(
            """
            QComboBox {
                background-color: #2b2b2b;
                color: #e8e8e8;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 13px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: #e8e8e8;
                selection-background-color: #3a7bd5;
            }
            """
        )
        for label, _ in self.LANGUAGES:
            self._lang_combo.addItem(label)
        lang_row.addWidget(lang_label)
        lang_row.addWidget(self._lang_combo)
        lang_row.addStretch()
        root.addLayout(lang_row)

        # Transcribe button
        self._btn_transcribe = QPushButton("Transcribe")
        self._btn_transcribe.setEnabled(False)
        self._btn_transcribe.setFixedHeight(40)
        self._btn_transcribe.setStyleSheet(
            """
            QPushButton {
                background-color: #3a7bd5;
                color: white;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover  { background-color: #5091e8; }
            QPushButton:pressed { background-color: #2960b0; }
            QPushButton:disabled { background-color: #555; color: #999; }
            """
        )
        self._btn_transcribe.clicked.connect(self._on_transcribe_clicked)
        root.addWidget(self._btn_transcribe)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        self._progress.setFixedHeight(22)
        root.addWidget(self._progress)

        # Status label
        self._status_label = QLabel("Ready.")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setStyleSheet("color: #aaa; font-size: 12px;")
        self._status_label.setWordWrap(True)
        root.addWidget(self._status_label)

        root.addStretch()

    # ------------------------------------------------------------------
    # Dark palette
    # ------------------------------------------------------------------

    def _apply_dark_palette(self) -> None:
        palette = QPalette()
        bg = QColor("#1a1a1a")
        fg = QColor("#e8e8e8")
        palette.setColor(QPalette.Window, bg)
        palette.setColor(QPalette.WindowText, fg)
        palette.setColor(QPalette.Base, QColor("#2b2b2b"))
        palette.setColor(QPalette.AlternateBase, QColor("#242424"))
        palette.setColor(QPalette.Text, fg)
        palette.setColor(QPalette.Button, QColor("#333"))
        palette.setColor(QPalette.ButtonText, fg)
        palette.setColor(QPalette.Highlight, QColor("#3a7bd5"))
        palette.setColor(QPalette.HighlightedText, QColor("#fff"))
        self.setPalette(palette)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_file_selected(self, path: str) -> None:
        """Validate and accept the dropped/selected file."""
        if not path.lower().endswith(".m4a"):
            QMessageBox.warning(
                self,
                "Unsupported File",
                f"Only .m4a files are accepted.\n\nYou dropped:\n{path}",
            )
            return

        if not os.path.isfile(path):
            QMessageBox.warning(self, "File Not Found", f"Cannot find file:\n{path}")
            return

        self._audio_path = path
        self._path_display.setText(path)
        self._path_display.setStyleSheet("color: #e8e8e8; font-size: 12px;")
        self._btn_transcribe.setEnabled(True)
        self._set_status("File ready. Click Transcribe to begin.")
        self._progress.setValue(0)

    def _on_transcribe_clicked(self) -> None:
        if not self._audio_path:
            return
        self._start_transcription(self._audio_path)

    def _start_transcription(self, audio_path: str) -> None:
        """Spin up a QThread + worker and begin transcription."""
        self._btn_transcribe.setEnabled(False)
        self._drop_zone.setEnabled(False)
        self._progress.setValue(0)
        self._set_status("Starting…")

        _, language = self.LANGUAGES[self._lang_combo.currentIndex()]

        self._thread = QThread(self)
        self._worker = TranscriptionWorker(audio_path, language)
        self._worker.moveToThread(self._thread)

        # Wire signals
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        # Cleanup after done
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._on_thread_finished)

        self._thread.start()

    # ------------------------------------------------------------------
    # Worker signal handlers
    # ------------------------------------------------------------------

    def _on_progress(self, percent: int, message: str) -> None:
        self._progress.setValue(percent)
        self._set_status(message)

    def _on_finished(self, txt_path: str, srt_path: str) -> None:
        self._progress.setValue(100)
        self._set_status(f"Saved:\n  {txt_path}\n  {srt_path}")
        QMessageBox.information(
            self,
            "Transcription Complete",
            f"Files saved successfully:\n\n• {txt_path}\n• {srt_path}",
        )

    def _on_error(self, message: str) -> None:
        self._progress.setValue(0)
        self._set_status("Transcription failed.")
        QMessageBox.critical(
            self,
            "Transcription Error",
            f"An error occurred during transcription:\n\n{message}",
        )

    def _on_thread_finished(self) -> None:
        self._btn_transcribe.setEnabled(True)
        self._drop_zone.setEnabled(True)
        # Clean up references
        self._worker = None
        self._thread = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_status(self, text: str) -> None:
        self._status_label.setText(text)

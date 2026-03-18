"""
Sound to Text - macOS Desktop Transcription App
Entry point: launches the PySide6 GUI application.
"""

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Sound to Text")
    app.setOrganizationName("SoundToText")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

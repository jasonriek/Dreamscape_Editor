import sys
from PySide6.QtWidgets import (QApplication)
from PySide6.QtGui import (QIcon)
from ds_main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    app.setWindowIcon(QIcon('icon_maybe_BIG.ico'))
    window = MainWindow()
    with open('resources/ds.qss', 'r') as qss:
        window.setStyleSheet(qss.read())
    window.showMaximized()
    sys.exit(app.exec())

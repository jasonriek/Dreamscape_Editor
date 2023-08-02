import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QStyledItemDelegate, QStyleOptionViewItem, QItemDelegate, QPushButton, QScrollArea, QVBoxLayout, QWidget, QDockWidget, QFileDialog,
QListWidget, QListWidgetItem, QCheckBox, QHBoxLayout, QListView, QStyle, QAbstractItemView, QMenu, QInputDialog, QMessageBox)

from PySide6.QtGui import QPixmap, QImage, QPainter, QMouseEvent, QAction, QIcon
from PySide6.QtCore import (Qt, QAbstractListModel, QModelIndex, QMimeData, QByteArray, QDataStream,
                            QIODevice, Signal, QEvent, QRect)

import dreamscape_config

from dreamscape_layers import (Layers)
from dreamscape_tiles import (TileSelector, TileCanvas)
from dreamscape_tools import (Tools, ActiveTileWidget)

dreamscape_config.tileset_layers.appendTilesetLayer('Cyber Punk 1','cyberpunk_1_assets_1.png',32,32)
dreamscape_config.tileset_layers.appendTilesetLayer('Cyber Punk 2','cyberpunk_1_assets_1.png',32,32)
dreamscape_config.tileset_layers.appendTilesetLayer('Cyber Punk 3','cyberpunk_1_assets_1.png',32,32)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        tile_selector = TileSelector()
        tile_selector.active_tile_widget = ActiveTileWidget()

        # Create and set up the TileSelector dock
        selector_dock = QDockWidget("Tile Selector", self)
        selector_dock.setWidget(tile_selector)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, selector_dock)

        # Create and set up the TileCanvas dock
        canvas_dock = QDockWidget("Tile Canvas", self)
        tile_canvas = TileCanvas(tile_selector)
        layers_widget = Layers(tile_canvas)
        tile_canvas.layers_widget = layers_widget
        scroll_area = QScrollArea()
        scroll_area.setWidget(tile_canvas)
        canvas_dock.setWidget(scroll_area)
        
        # Create and set up the ToolDock
        tool_dock = QDockWidget("Tools", self)
        tools = Tools(tile_selector, tile_canvas, layers_widget)
        tools.addToLayout(tile_selector.active_tile_widget)
        tools.setInternalWidgets()
        tool_dock.setWidget(tools)
        
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, tool_dock)
        layers_dock = QDockWidget('Layers', self)
        layers_dock.setWidget(layers_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, canvas_dock)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, layers_dock)
        self.setWindowTitle("Dreamscape Editor")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon_maybe_BIG.ico'))

    window = MainWindow()
    with open('ds.qss', 'r') as qss:
        window.setStyleSheet(qss.read())
    window.showMaximized()
    sys.exit(app.exec())

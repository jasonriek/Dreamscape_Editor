from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)

from .load_tileset_widget import LoadTilesetWidget

import ds


class TilesetPropertiesWidget(QWidget):
    def __init__(self, tileset_tab_bar, tile_canvas, layers):
        super().__init__()

        self._layout = QVBoxLayout(self)
        self.tileSetLoader = LoadTilesetWidget(tileset_tab_bar, tile_canvas, layers)
        self.tile_canvas = tile_canvas
        self.tile_selector = tileset_tab_bar.tile_selector

        self._layout.addWidget(self.tileSetLoader)
        self.initTileTable()
        self.initExportButton()

    def initTileTable(self):
        self.tileTable = QTableWidget(2, 1)
        self.tileTable.setHorizontalHeaderLabels(["Tile Information"])
        self.tileTable.setVerticalHeaderLabels(["World Coord.", "Tile Selection"])
        self.tileTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tileTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.tile_selector.tileSelected.connect(self.setTileXYInTileTable)
        self.tile_canvas.mouseMoved.connect(self.setWorldXYInTileTable)

        self._layout.addWidget(self.tileTable)

    def initExportButton(self):
        self.exportJsonButton = QPushButton('Export JSON')
        self.exportJsonButton.clicked.connect(self.exportJson)
        self._layout.addWidget(self.exportJsonButton)

    def setTileXYInTileTable(self, x, y):
        self.tileTable.setItem(0, 1, QTableWidgetItem(f"({x}, {y})"))

    def setWorldXYInTileTable(self, x, y):
        self.tileTable.setItem(0, 0, QTableWidgetItem(f"({x}, {y})"))

    def exportJson(self):
        with open('test.json', 'w') as f, open('test_overlay.json', 'w') as fo:
            game, game_overlay = ds.data.layers.getJson()
            f.write(game)
            fo.write(game_overlay)

    def addToLayout(self, widget):
        self._layout.addWidget(widget)
from PySide6.QtWidgets import (QStatusBar, QWidget, QSizePolicy, QHBoxLayout, QLabel)

from .load_tileset_widget import LoadTilesetWidget

class TilesetProperties:
    def __init__(self, tileset_tab_bar, tile_canvas, layers):
        super().__init__()

        self.tileset_loader = LoadTilesetWidget(tileset_tab_bar, tile_canvas, layers)
        self.tile_canvas = tile_canvas
        self.tile_selector = tileset_tab_bar.tile_selector
        self.world_coord_label = QLabel('World Coordinates: ')
        self.tileset_coord_label = QLabel('Tile Selection: ')

        self.status_bar = QStatusBar()
        self.status_widget = QWidget()
        self.status_bar.addWidget(self.status_widget)
        self.status_bar_layout = QHBoxLayout(self.status_widget)

        self.status_bar_layout.addWidget(self.world_coord_label)
        status_bar_filler = QWidget()
        status_bar_filler.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.status_bar_layout.addWidget(status_bar_filler)

        self.tile_selector.tileSelected.connect(self.setTileXYInTileTable)
        self.tile_canvas.mouseMoved.connect(self.setWorldXYInTileTable)

    def setWorldXYInTileTable(self, x, y):
        self.world_coord_label.setText(f'World Coordinates: ({x}, {y})')

    def setTileXYInTileTable(self, x, y):
        self.tileset_coord_label.setText(f'Tile Selection: ({x}, {y})')
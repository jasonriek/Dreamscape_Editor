from PySide6.QtWidgets import (QStatusBar, QWidget, QPushButton, QSizePolicy, QGroupBox, QHBoxLayout, QSpinBox, QLabel)

from .load_tileset_widget import LoadTilesetWidget

import ds


class TilesetProperties:
    def __init__(self, tileset_tab_bar, tile_canvas, layers):
        super().__init__()

        self.tileset_loader = LoadTilesetWidget(tileset_tab_bar, tile_canvas, layers)
        self.tile_canvas = tile_canvas
        self.tile_selector = tileset_tab_bar.tile_selector
        self.world_coord_label = QLabel('(0, 0)')
        self.tileset_coord_label = QLabel('(0, 0)')
        self.tile_width_spinbox = QSpinBox()
        self.tile_height_spinbox = QSpinBox()
        self.tile_width_spinbox.setMinimum(1)
        self.tile_height_spinbox.setMinimum(1)
        self.tile_width_spinbox.setValue(32)
        self.tile_height_spinbox.setValue(32)
        
        self.tile_size_buttons = [QPushButton(str(2**i)) for i in range(3, 7)]
        self.tile_size_gbox = QGroupBox()
        self.tile_size_layout = QHBoxLayout(self.tile_size_gbox)
        for button in self.tile_size_buttons:
            button.setFixedWidth(32)
            button.clicked.connect(self.setTileSize(int(button.text())))
            self.tile_size_layout.addWidget(button)
        tile_width_label = QLabel(' Tile Width: ')
        tile_height_label = QLabel(' Tile Height: ')
        self.tile_size_layout.addWidget(tile_width_label)
        self.tile_size_layout.addWidget(self.tile_width_spinbox)
        self.tile_size_layout.addWidget(tile_height_label)
        self.tile_size_layout.addWidget(self.tile_height_spinbox)
        
        self.tileset_coord_gbox = QGroupBox()
        self.tileset_coord_layout = QHBoxLayout(self.tileset_coord_gbox)
        self.tileset_coord_layout.addWidget(self.tileset_coord_label)


        self.tile_width_spinbox.valueChanged.connect(self.setTileWidth)
        self.tile_height_spinbox.valueChanged.connect(self.setTileHeight)

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
        self.world_coord_label.setText(f'({x}, {y})')

    def setTileXYInTileTable(self, x, y):
        self.tileset_coord_label.setText(f'({x}, {y})')
    
    def setTileWidth(self, width:int):
        ds.data.world.tile_width = width
    
    def setTileHeight(self, height:int):
        ds.data.world.tile_height = height

    def setTileSize(self, size:int):
        def _setTileSize():
            self.tile_width_spinbox.setValue(size)
            self.tile_height_spinbox.setValue(size)
        return _setTileSize 
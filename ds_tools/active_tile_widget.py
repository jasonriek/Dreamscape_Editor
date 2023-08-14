from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QGroupBox, 
    QSizePolicy, QCheckBox)

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Signal

import ds


class ActiveTileWidget(QWidget):
    worldTileClicked = Signal(int, int)
    def __init__(self, tile_canvas):
        super().__init__()
        self.tile_canvas = tile_canvas
        # Initialize the active tile display and checkbox
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        
        self.setupSelectedTileGroup()
        self.setupBaseTileGroup()

        layout.addWidget(self.gbox1)
        layout.addWidget(self.gbox2)

        self.setLayout(layout)

    def setupSelectedTileGroup(self):
        self.gbox1 = QGroupBox(self)
        self.gbox1_layout = QHBoxLayout()

        label1 = QLabel('Selected Tile:')
        self.active_tile_label = QLabel()
        self.active_tile_label.setFixedSize(32, 32)
        
        self.base_tile_button = QPushButton("Set as base tile")
        self.base_tile_button.clicked.connect(self.setBaseTile)
        self.hide_base_tile_checkbox = QCheckBox('Hide')
        self.hide_base_tile_checkbox.stateChanged.connect(self.hideBaseTiles)
        
        filler_1 = QWidget()
        filler_1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.collision_checkbox = QCheckBox('Has Collision')
        self.overlay_checkbox = QCheckBox('Overlay')
        
        widgets = [
            label1, 
            self.active_tile_label, 
            self.base_tile_button, 
            filler_1, 
            self.collision_checkbox, 
            self.overlay_checkbox
        ]

        for widget in widgets:
            self.gbox1_layout.addWidget(widget)

        self.gbox1.setLayout(self.gbox1_layout)

    def setupBaseTileGroup(self):
        self.gbox2 = QGroupBox(self)
        self.gbox2_layout = QHBoxLayout()

        label2 = QLabel('Base Tile:')
        self.base_tile_label = QLabel()
        self.base_tile_label.setFixedSize(32, 32)
        
        filler_2 = QWidget()
        filler_2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        widgets = [label2, self.base_tile_label, self.hide_base_tile_checkbox, filler_2]

        for widget in widgets:
            self.gbox2_layout.addWidget(widget)

        self.gbox2.setLayout(self.gbox2_layout)

    def updateActiveTileDisplay(self, image):
        pixmap = QPixmap.fromImage(image)
        self.active_tile_label.setPixmap(pixmap)
    
    def setBaseTile(self):
        self.base_tile_label.setPixmap(self.active_tile_label.pixmap().copy())
        ds.data.layers.base_tile_src = ds.data.layers.active_layer_src
        ds.data.layers.base_tile_src_x = ds.data.world.selected_tile_x
        ds.data.layers.base_tile_src_y = ds.data.world.selected_tile_y
        ds.data.layers.base_tile_src_w = 32
        ds.data.layers.base_tile_src_h = 32
        self.tile_canvas.drawBaseTiles()
        self.tile_canvas.redrawWorld()
        self.tile_canvas.update()
    
    def hideBaseTiles(self, hide):
        ds.data.layers.base_tiles_visible = not bool(hide)
        if ds.data.layers.base_pixmap:
            self.tile_canvas.redrawWorld()
            self.tile_canvas.update()

    def updateTileProperties(self, tile):
        self.worldTileClicked.emit(tile[0], tile[1])
        self.collision_checkbox.setChecked(bool(tile[4]))
        self.overlay_checkbox.setChecked(bool(tile[5]))  
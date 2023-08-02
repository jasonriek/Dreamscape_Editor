from PySide6.QtWidgets import (QWidget, QSizePolicy, QTabBar, QVBoxLayout)
from PySide6.QtGui import (QPainter, QPixmap, QMouseEvent, QImage)
from PySide6.QtCore import (Qt, Signal)

import dreamscape_config

class TileSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(672, 352)
        self.selected_tile = None
        self.active_tile_widget = None
    
    def changeTileset(self, name:str, path:str):
        dreamscape_config.tileset_layers.active_layer_name = name
        dreamscape_config.tileset_layers.active_layer_path = path
        self.tileset = QImage(path)
        self.update()

    def setTileset(self, name:str, path:str):
        dreamscape_config.tileset_layers.appendTilesetLayer(name, path, 32, 32)
        self.changeTileset(name, path)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw checkered background
        for x in range(0, self.width(), dreamscape_config.CHECKER_SIZE):
            for y in range(0, self.height(), dreamscape_config.CHECKER_SIZE):
                if (x // dreamscape_config.CHECKER_SIZE) % 2 == 0:
                    color = dreamscape_config.WHITE if (y // dreamscape_config.CHECKER_SIZE) % 2 == 0 else dreamscape_config.LIGHT_GRAY
                else:
                    color = dreamscape_config.LIGHT_GRAY if (y // dreamscape_config.CHECKER_SIZE) % 2 == 0 else dreamscape_config.WHITE

                painter.fillRect(x, y, dreamscape_config.CHECKER_SIZE, dreamscape_config.CHECKER_SIZE, color)

        painter.drawImage(0, 0, self.tileset)

        if self.selected_tile:
            tile_x, tile_y = self.selected_tile
            painter.setPen(Qt.GlobalColor.red)
            painter.drawRect(tile_x * dreamscape_config.TILE_SIZE, tile_y * dreamscape_config.TILE_SIZE, dreamscape_config.TILE_SIZE, dreamscape_config.TILE_SIZE)

    def mousePressEvent(self, event: QMouseEvent):
        x = int(event.position().x()) // dreamscape_config.TILE_SIZE
        y = int(event.position().y()) // dreamscape_config.TILE_SIZE
        dreamscape_config.tileset_layers.selected_x = x
        dreamscape_config.tileset_layers.selected_y = y
        self.selected_tile = (x, y)
        if self.selected_tile:
                tile_x, tile_y = self.selected_tile
                tile_pixmap = self.tileset.copy(tile_x * dreamscape_config.TILE_SIZE, 
                                                tile_y * dreamscape_config.TILE_SIZE, 
                                                dreamscape_config.TILE_SIZE, 
                                                dreamscape_config.TILE_SIZE)
                # Assuming you have a reference to the ActiveTileWidget instance
        self.active_tile_widget.update_active_tile_display(tile_pixmap)

        self.update()  # Trigger a repaint

    def get_selected_tile(self):
        return self.selected_tile

class TilesetBar(QWidget):
    tilesetChanged = Signal(str)
    def __init__(self):
        super().__init__()

        # Create the TileSelector and QTabBar
        self.tile_selector = TileSelector()
        self.tab_bar = QTabBar()

        # Connect tab change to update function
        self.tab_bar.currentChanged.connect(self.changeTileset)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_bar)
        layout.addWidget(self.tile_selector)
        self.setLayout(layout)

        # Dictionary to store tilesets paths associated with tab indexes
        self.tilesets = {}

        self.addTileset('Cyber Punk 1', 'cyberpunk_1_assets_1.png')
    
    def changeIndexByTilesetPath(self, tileset_path):
        for i in range(self.tab_bar.count()):
            if self.tilesets[i][1] == tileset_path:
                self.tab_bar.setCurrentIndex(i)
                break

    def addTileset(self, tileset_name, tileset_path):
        self.tile_selector.setTileset(tileset_name, tileset_path)
        index = self.tab_bar.addTab(tileset_name)
        self.tilesets[index] = (tileset_name, tileset_path)
        # If it's the first tileset, set it immediately
        if self.tab_bar.count() == 1:
            self.changeTileset(0)

    def changeTileset(self, index):
        tileset_data = self.tilesets.get(index)
        if tileset_data:
            self.tile_selector.changeTileset(tileset_data[0], tileset_data[1])
            self.tilesetChanged.emit(tileset_data[1])

class TileCanvas(QWidget):
    def __init__(self, tileset_bar):
        super().__init__()
        self.tile_selector = tileset_bar.tile_selector
        self.setFixedSize(dreamscape_config.DISPLAY_WIDTH, dreamscape_config.DISPLAY_HEIGHT)
        self.show_grid = True
        dreamscape_config.tileset_layers.layer_pixmaps = [QPixmap(dreamscape_config.DISPLAY_WIDTH, dreamscape_config.DISPLAY_HEIGHT) for _ in range(dreamscape_config.tileset_layers.length())]
        for pixmap in dreamscape_config.tileset_layers.layer_pixmaps:
            pixmap.fill(Qt.GlobalColor.transparent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Paint tiles from all layers based on visibility
        for layer_index in reversed(range(len(dreamscape_config.tileset_layers.layer_pixmaps))):
            pixmap = dreamscape_config.tileset_layers.layer_pixmaps[layer_index]
            if dreamscape_config.tileset_layers.layer_visibilty[layer_index]:  # Check if this layer should be rendered
                painter.drawPixmap(0, 0, pixmap)

        # Draw the grid if the flag is set
        if self.show_grid:
            painter.setPen(Qt.GlobalColor.black)
            for x in range(0, dreamscape_config.DISPLAY_WIDTH, dreamscape_config.TILE_SIZE):
                painter.drawLine(x, 0, x, dreamscape_config.DISPLAY_HEIGHT)
            for y in range(0, dreamscape_config.DISPLAY_HEIGHT, dreamscape_config.TILE_SIZE):
                painter.drawLine(0, y, dreamscape_config.DISPLAY_WIDTH, y)
        painter.end()

    def draw_tile_on_layer(self, tileset_name, tile_index):
        tile_data = dreamscape_config.tileset_layers.tile(tileset_name, tile_index)
        if tile_data:
            src_x, src_y, x, y, b = tile_data
            tileset_info = dreamscape_config.tileset_layers.tilesetLayer(tileset_name)
            tileset_img = QImage(tileset_info['tileset'])
            painter = QPainter(dreamscape_config.tileset_layers.layer_pixmaps[dreamscape_config.tileset_layers.layerIndex(tileset_name)])  # Assuming you have one QPixmap per tileset layer
            painter.drawImage(x * tileset_info['tile_width'], y * tileset_info['tile_height'],
                      tileset_img,
                      src_x * tileset_info['tile_width'], src_y * tileset_info['tile_height'],
                      tileset_info['tile_width'], tileset_info['tile_height'])
            painter.end()  # End painting

    def redraw_world(self):
        for tileset_name in dreamscape_config.tileset_layers.order:
            self.redraw_layer(tileset_name)

    def redraw_layer(self, tileset_name):
        tileset_info = dreamscape_config.tileset_layers.tilesetLayer(tileset_name)
        tileset_img = QImage(tileset_info['tileset'])
        
        pixmap = QPixmap(dreamscape_config.DISPLAY_WIDTH, dreamscape_config.DISPLAY_HEIGHT)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        
        for i, tile_data in enumerate(tileset_info['tiles']):
            src_x, src_y, x, y, b = tile_data
            painter.drawImage(x * dreamscape_config.TILE_SIZE, y * dreamscape_config.TILE_SIZE,
                            tileset_img,
                            src_x * tileset_info['tile_width'], src_y * tileset_info['tile_height'],
                            tileset_info['tile_width'], tileset_info['tile_height'])
        dreamscape_config.tileset_layers.layer_pixmaps[dreamscape_config.tileset_layers.layerIndex(tileset_name)] = pixmap
        painter.end()  # End painting

    def swap_layers(self, layer1_index, layer2_index):
        # Swap the tilesets in TilesetLayers
        success = dreamscape_config.tileset_layers.swapLayerOrder(layer1_index, layer2_index)
        if not success:
            print(f"Failed to swap layers: {layer1_index} and {layer2_index}")
            return

        # Redraw every layer to ensure correct stacking order
        for tileset_name in dreamscape_config.tileset_layers.order:
            self.redraw_layer(tileset_name)
        self.update()  # Trigger a repaint

    def mousePressEvent(self, event: QMouseEvent):
        if not self.tile_selector.get_selected_tile():
            return

        x = int(event.position().x()) // dreamscape_config.TILE_SIZE
        y = int(event.position().y()) // dreamscape_config.TILE_SIZE

        # Check if tile already exists here at this layer, if so, replace it.
        current_layer_index = dreamscape_config.tileset_layers.layerIndex(dreamscape_config.tileset_layers.active_layer_name)
        tile_index = dreamscape_config.tileset_layers.getTileIndexFromXY(x, y)
        if tile_index is not None and tile_index >= 0: # update the current tile
            dreamscape_config.tileset_layers.updateTile(dreamscape_config.tileset_layers.active_layer_name, tile_index,
                [dreamscape_config.tileset_layers.selected_x,
                dreamscape_config.tileset_layers.selected_y,
                x,
                y,
                0]
            )
            # Redraw every layer to ensure correct stacking order
            for tileset_name in dreamscape_config.tileset_layers.order:
                self.redraw_layer(tileset_name)
        else: # make a new tile
            tile_index = dreamscape_config.tileset_layers.appendTile(
                dreamscape_config.tileset_layers.active_layer_name, 
                dreamscape_config.tileset_layers.selected_x, 
                dreamscape_config.tileset_layers.selected_y,
                x,
                y,
                0)
        if current_layer_index is not None:
            # Register the tile drawing as an operation for the selected layer
            self.draw_tile_on_layer(dreamscape_config.tileset_layers.active_layer_name, tile_index)
            self.update()  # Trigger a repaint

    def update_layer_visibility(self):
        self.update()  # Trigger repaint



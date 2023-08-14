from PySide6.QtWidgets import (QWidget, QSizePolicy)
from PySide6.QtGui import (QImage, QMouseEvent, QPainter, QColor)
from PySide6.QtCore import (Qt, Signal, QRect)

import ds


class TileSelector(QWidget):
    tileSelected = Signal(int, int)
    def __init__(self):
        super().__init__()
        self.selected_tiles = []  # List of (x, y) tile coordinates
        self.selected_tile_pixmap = None
        self.selected_tiles_pixmap = None
        self.drag_start = None  # Coordinate where dragging starts
        self.drag_rectangle = None
        self.start_drag_x = 0
        self.start_drag_y = 0
        self.active_tile_widget = None
        self.show_grid = False

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def toggleGrid(self, state=1):
        self.show_grid = bool(state)
        self.update()
    
    def changeTileset(self, name:str, path:str):
        ds.data.layers.active_layer_name = name
        ds.data.layers.active_layer_src = path
        self.tileset = QImage(path)
        self.setFixedSize(self.tileset.width(), self.tileset.height())
        self.update()

    def setTileset(self, name:str, path:str):
        ds.data.layers.setting_tileset = True
        ds.data.layers.appendTilesetLayer(name, path, ds.data.world.tile_width, ds.data.world.tile_height)
        self.changeTileset(name, path)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw checkered background
        for x in range(0, self.width(), ds.data.CHECKER_SIZE):
            for y in range(0, self.height(), ds.data.CHECKER_SIZE):
                if (x // ds.data.CHECKER_SIZE) % 2 == 0:
                    color = ds.data.WHITE if (y // ds.data.CHECKER_SIZE) % 2 == 0 else ds.data.LIGHT_GRAY
                else:
                    color = ds.data.LIGHT_GRAY if (y // ds.data.CHECKER_SIZE) % 2 == 0 else ds.data.WHITE

                painter.fillRect(x, y, ds.data.CHECKER_SIZE, ds.data.CHECKER_SIZE, color)

        painter.drawImage(0, 0, self.tileset)

        # Draw the grid if the flag is set
        if self.show_grid:
            painter.setPen(Qt.GlobalColor.black)
            for x in range(0, self.width(), ds.data.TILE_SIZE):
                painter.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), ds.data.TILE_SIZE):
                painter.drawLine(0, y, self.width(), y)
        
        if self.drag_rectangle:
            painter.setBrush(QColor(0, 255, 0, 75))
            painter.setPen(QColor(0, 255, 0))  # Set to green color
            painter.drawRect(self.drag_rectangle)

        if self.selected_tiles:
            painter.setBrush(QColor(0, 255, 0, 75))
            painter.setPen(QColor(0, 255, 0))  # Set to green color
            for tile in self.selected_tiles:
                painter.drawRect(
                    tile[0] * ds.data.world.tile_width, 
                    tile[1] * ds.data.world.tile_height, 
                    ds.data.world.tile_width, 
                    ds.data.world.tile_height
                )

        painter.end()

    def selectTileFromDropper(self, x, y):
        self.selectTile(x, y)
        self.selected_tiles_pixmap = self.selected_tile_pixmap
        self.selected_tiles = [(x, y)]

    def selectTile(self, x, y):
        # Emitting only the first tile in this case, modify as needed
        if self.selected_tiles:
            ds.data.world.selected_tile_x = x
            ds.data.world.selected_tile_y = y
            self.selected_tile_pixmap = self.tileset.copy(
                x * ds.data.world.tile_width, 
                y * ds.data.world.tile_height, 
                ds.data.world.tile_width, 
                ds.data.world.tile_height
            )
            self.tileSelected.emit(x, y)
            self.active_tile_widget.updateActiveTileDisplay(self.selected_tile_pixmap)
            self.update()

    def calculateDragArea(self, event:QMouseEvent):
        """Fill tiles in the rectangular drag area."""
        x = int(event.position().x()) // ds.data.world.tile_width
        y = int(event.position().y()) // ds.data.world.tile_height
        distance_from_start_x = x - self.start_drag_x
        distance_from_start_y = y - self.start_drag_y

        # Determine the starting and ending points based on drag direction
        self.fill_x_start, self.fill_x_end = (self.start_drag_x, x) if distance_from_start_x >= 0 else (x, self.start_drag_x)
        self.fill_y_start, self.fill_y_end = (self.start_drag_y, y) if distance_from_start_y >= 0 else (y, self.start_drag_y)

        self.drag_rectangle = QRect(
            self.fill_x_start * ds.data.world.tile_width,
            self.fill_y_start * ds.data.world.tile_height,
            (self.fill_x_end - self.fill_x_start + 1) * ds.data.world.tile_width,
            (self.fill_y_end - self.fill_y_start + 1) * ds.data.world.tile_height
        )
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.calculateDragArea(event)

    def mousePressEvent(self, event: QMouseEvent):
        x = int(event.position().x()) // ds.data.world.tile_width
        y = int(event.position().y()) // ds.data.world.tile_height
        self.start_drag_x = x
        self.start_drag_y = y
        self.calculateDragArea(event)
        self.drag_start = (x, y)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        end_x = int(event.position().x()) // ds.data.world.tile_width
        end_y = int(event.position().y()) // ds.data.world.tile_height

        start_x, start_y = self.drag_start

        # Determine top-left and bottom-right corners
        tl_x, br_x = sorted([start_x, end_x])
        tl_y, br_y = sorted([start_y, end_y])
        self.selected_tiles = [(x, y) for x in range(tl_x, br_x+1) for y in range(tl_y, br_y+1)]
        max_x = max([t[0] for t in self.selected_tiles])
        max_y = max([t[1] for t in self.selected_tiles])
        min_x = min([t[0] for t in self.selected_tiles])
        min_y = min([t[1] for t in self.selected_tiles])
        x_len = abs(max_x - min_x) + 1
        y_len = abs(max_y - min_y) + 1

        self.selected_tiles_pixmap = self.tileset.copy(
            min_x * ds.data.world.tile_width, 
            min_y * ds.data.world.tile_height, 
            ds.data.world.tile_width * x_len, 
            ds.data.world.tile_height * y_len
        )
        
        self.drag_rectangle = None
        self.selectTile(start_x, start_y)
        self.update()

    def getSelectedTile(self):
        if len(self.selected_tiles) > 0:
            return self.selected_tiles[0]
        return None
    
    def getSelectedTiles(self):
        return self.selected_tiles
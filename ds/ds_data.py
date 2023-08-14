
from PySide6.QtCore import (Qt)

from .ds_layers_data import LayersData
from .ds_paint_tools_data import PaintToolsData
from .ds_world_data import WorldData


class Data:
    TILE_SIZE = 32
    WORLD_WIDTH = 150
    WORLD_HEIGHT = 150
    DISPLAY_WIDTH = TILE_SIZE * WORLD_WIDTH
    DISPLAY_HEIGHT = TILE_SIZE * WORLD_HEIGHT
    MAX_HISTORY_SIZE = 10
    CHECKER_SIZE = 16
    LIGHT_GRAY = Qt.GlobalColor.lightGray
    WHITE = Qt.GlobalColor.white
    def __init__(self):
        self.layers = LayersData(self)
        self.paint_tools = PaintToolsData(self)
        self.world = WorldData(self)

data = Data()

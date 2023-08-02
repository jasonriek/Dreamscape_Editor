from PySide6.QtCore import Qt
from dreamscape_tileset_data import TilesetLayers

TILE_SIZE = 32
WORLD_WIDTH = 150
WORLD_HEIGHT = 150
DISPLAY_WIDTH = TILE_SIZE * WORLD_WIDTH
DISPLAY_HEIGHT = TILE_SIZE * WORLD_HEIGHT

CHECKER_SIZE = 16
LIGHT_GRAY = Qt.GlobalColor.lightGray
WHITE = Qt.GlobalColor.white

tileset_layers = TilesetLayers()
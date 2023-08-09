import pickle
import copy
from PySide6.QtCore import (Qt, QBuffer, QByteArray, QIODevice)
from PySide6.QtGui import (QPixmap)
from dreamscape_tileset_data import TilesetLayers

TILE_SIZE = 32
WORLD_WIDTH = 150
WORLD_HEIGHT = 150
DISPLAY_WIDTH = TILE_SIZE * WORLD_WIDTH
DISPLAY_HEIGHT = TILE_SIZE * WORLD_HEIGHT
MAX_HISTORY_SIZE = 10

CHECKER_SIZE = 16
LIGHT_GRAY = Qt.GlobalColor.lightGray
WHITE = Qt.GlobalColor.white

def pixmapToBytes(pixmap):
    if pixmap is None:
        return None
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.save(buffer, "PNG")
    return byte_array.data()
    
def bytesToPixmap(data):
    if data is None:
        return None
    pixmap = QPixmap()
    pixmap.loadFromData(data, "PNG")
    return pixmap

def saveToFile(tileset_layers:TilesetLayers, file_name:str):
    print("Saving: ", len(tileset_layers.layer_pixmaps))
    _tileset_layers = copy.deepcopy(tileset_layers)
    print("Saving: ", len(_tileset_layers.layer_pixmaps))
    # Convert QPixmaps to bytes
    _tileset_layers.layer_pixmaps = [pixmapToBytes(pixmap) for pixmap in _tileset_layers.layer_pixmaps]
    _tileset_layers.base_pixmap = pixmapToBytes(_tileset_layers.base_pixmap)
        
    with open(file_name, 'wb') as f:
        pickle.dump(_tileset_layers, f)

def loadFromFile(path:str):
    tileset_layers = None
    with open(path, 'rb') as f:
        tileset_layers:TilesetLayers = pickle.load(f)
        print("Loaded: ", len(tileset_layers.layer_pixmaps))

    if tileset_layers:
        # Convert bytes back to QPixmaps
        tileset_layers.layer_pixmaps = [bytesToPixmap(data) for data in tileset_layers.layer_pixmaps]
        tileset_layers.base_pixmap = bytesToPixmap(tileset_layers.base_pixmap)

    return tileset_layers

class PaintTools:
    PENCIL = 0
    BRUSH = 1
    DRAG_DRAW = 2
    DRAG = 3
    BUCKET = 4
    DROPPER = 5
    ERASER = 6
    SELECT = 7

    def __init__(self):
        self.selection = 0

    def changeSelection(self, tool_name:str):
        selelections = {
            'Pencil': self.PENCIL,
            'Brush': self.BRUSH,
            'Drag & Draw': self.DRAG_DRAW,
            'Drag': self.DRAG,
            'Bucket Fill': self.BUCKET,
            'Dropper': self.DROPPER,
            'Eraser': self.ERASER,
            'Select': self.SELECT
        }
        self.selection = selelections.get(tool_name, self.SELECT)
    
    def isDrawingTool(self, tool=None):
        if tool is None:
            tool = self.selection
        return {
            PENCIL: True,
            BRUSH: True,
            DRAG_DRAW: True,
        }.get(tool, False)
        


PENCIL = PaintTools.PENCIL
BRUSH = PaintTools.BRUSH
DRAG_DRAW = PaintTools.DRAG_DRAW
DRAG = PaintTools.DRAG
BUCKET = PaintTools.BUCKET
DROPPER = PaintTools.DROPPER
ERASER = PaintTools.ERASER
SELECT = PaintTools.SELECT


tileset_layers = TilesetLayers()
paint_tools = PaintTools()
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

class PaintTools:
    PENCIL = 0
    BRUSH = 1
    DRAG_DRAW = 2
    DRAG = 3
    BUCKET = 4
    DROPPER = 5
    ERASER = 6

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
            'Eraser': self.ERASER
        }
        self.selection = selelections.get(tool_name)
    
    def isDrawingTool(self, tool=None):
        if tool is None:
            tool = self.selection
        return {
            PENCIL: True,
            BRUSH: True,
            DRAG_DRAW: True,
            BUCKET: True
        }.get(tool, False)
        


PENCIL = PaintTools.PENCIL
BRUSH = PaintTools.BRUSH
DRAG_DRAW = PaintTools.DRAG_DRAW
DRAG = PaintTools.DRAG
BUCKET = PaintTools.BUCKET
DROPPER = PaintTools.DROPPER
ERASER = PaintTools.ERASER


tileset_layers = TilesetLayers()
paint_tools = PaintTools()
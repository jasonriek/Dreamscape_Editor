

class PaintToolsData:
    PENCIL = 0
    BRUSH = 1
    DRAG_DRAW = 2
    DRAG = 3
    BUCKET = 4
    DROPPER = 5
    ERASER = 6
    SELECT = 7

    def __init__(self, parent=None):
        self.parent = parent
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
            self.PENCIL: True,
            self.BRUSH: True,
            self.DRAG_DRAW: True,
        }.get(tool, False)
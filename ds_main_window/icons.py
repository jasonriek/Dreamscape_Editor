from PySide6.QtGui import (QIcon, QCursor, QPixmap)
from PySide6.QtCore import (Qt, QRect, QSize)


class Icons:
    def __init__(self, main_window):
        self.main_window = main_window
        self.icons = QPixmap('resources/paint_tool_icons.png')
        self.mouse_icon = QPixmap('resources/mouse.png')

    def setDefaultCursor(self):
        self.main_window.tile_canvas.setCursor(Qt.CursorShape.ArrowCursor)

    def defaultMouseIcon(self):
        clip_space = QRect(0, 0, 32, 6432)
        clipped = self.mouse_icon.copy(clip_space)
        scaled = clipped.scaled(QSize(20, 20), Qt.AspectRatioMode.KeepAspectRatio)
        icon = QIcon()
        icon.addPixmap(scaled)
        return icon

    def setDropperIcon(self):
        self.setToolCursorIcon(64*4, 0)

    def setToolCursorIcon(self, x, y, w=64, h=64):
        clip_space = QRect(x, y, w, h)
        clipped = self.icons.copy(clip_space)
        self.scaled_pix = clipped.scaled(QSize(20, 20), Qt.AspectRatioMode.KeepAspectRatio)
        self.current_cursor = QCursor(self.scaled_pix, -1, -1)
        self.main_window.tile_canvas.setCursor(self.current_cursor)

    def setCursorIconByTool(self, tool_name:str):
        if tool_name == 'Pencil':
            self.setToolCursorIcon(0, 0)
        elif tool_name == 'Brush':
            self.setToolCursorIcon(64*3, 0)
        elif tool_name == 'Drag & Draw':
            self.setToolCursorIcon(64, 0)
        elif tool_name == 'Drag':
            self.setToolCursorIcon(64*2, 0)
        elif tool_name == 'Bucket Fill':
            self.setToolCursorIcon(64*5, 0)
        elif tool_name == 'Eraser':
            self.setToolCursorIcon(64*6, 0)
        elif tool_name == 'Dropper':
            self.setToolCursorIcon(64*4, 0)
        elif tool_name == 'Select':
            self.setDefaultCursor()

    def toolIcon(self, x, y, w=64, h=64):
        '''Returns the tool icon from the .png file at the selected coordinates.'''
        clip_space = QRect(x, y, w, h)
        clipped = self.icons.copy(clip_space)
        icon = QIcon()
        icon.addPixmap(clipped)
        return icon
    
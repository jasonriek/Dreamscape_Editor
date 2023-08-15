from PySide6.QtWidgets import (QMainWindow, QToolBar, QWidget, QScrollArea, QMenu, QDockWidget, 
                               QCheckBox, QVBoxLayout, QSizePolicy, QFileDialog)
from PySide6.QtGui import (QAction, QIcon, QKeySequence, QCursor, QPixmap, QActionGroup)
from PySide6.QtCore import (Qt, QRect, QSize)

import ds


class Toolbar:
    def __init__(self, main_window):
        self.main_window = main_window
        self.icons = self.main_window.icons

    def setup(self):
        # Create the toolbar
        self.toolbar = QToolBar('Paint Tools', self.main_window)
        self.main_window.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        # Select Mode
        self.select_action = QAction(self.icons.defaultMouseIcon(), 'Select')
        self.select_action.setCheckable(True)
        self.select_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.select_action)

        # Tile Pencil Brush
        self.pencil_action = QAction(self.icons.toolIcon(0, 0), 'Pencil')
        self.pencil_action.setCheckable(True)
        self.pencil_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.pencil_action)

        # Tile Paint Brush
        self.brush_action = QAction(self.icons.toolIcon(64*3, 0), 'Brush')
        self.brush_action.setCheckable(True)
        self.brush_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.brush_action)

        # Drag and Draw
        self.drag_draw_action = QAction(self.icons.toolIcon(64, 0), 'Drag & Draw')
        self.drag_draw_action.setCheckable(True)
        self.drag_draw_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.drag_draw_action)

        # Drag
        self.drag_action = QAction(self.icons.toolIcon(64*2, 0), 'Drag')
        self.drag_action.setCheckable(True)
        self.drag_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.drag_action)

        # Paint Bucket
        self.bucket_action = QAction(self.icons.toolIcon(64*5, 0), 'Bucket Fill')
        self.bucket_action.setCheckable(True)
        self.bucket_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.bucket_action)

        # Dropper
        self.dropper_action = QAction(self.icons.toolIcon(64*4, 0), 'Dropper')
        self.dropper_action.setCheckable(True)
        self.dropper_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.dropper_action)

        # Eraser
        self.eraser_action = QAction(self.icons.toolIcon(64*6, 0), 'Eraser')
        self.eraser_action.setCheckable(True)
        self.eraser_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.eraser_action)

        # Ensure only one toggle button can be active at a time
        self.tool_group = QActionGroup(self.main_window)
        self.tool_group.addAction(self.select_action)
        self.tool_group.addAction(self.pencil_action)
        self.tool_group.addAction(self.brush_action)
        self.tool_group.addAction(self.drag_draw_action)
        self.tool_group.addAction(self.drag_action)
        self.tool_group.addAction(self.bucket_action)
        self.tool_group.addAction(self.dropper_action)
        self.tool_group.addAction(self.eraser_action)
        self.tool_group.setExclusive(True)

    def tool(self):
        tool_id = ds.data.paint_tools.selection
        tool = self.pencil_action.toggle()   
        if tool_id == ds.data.paint_tools.PENCIL:
            tool = self.pencil_action.toggle()
        elif tool_id == ds.data.paint_tools.BRUSH:
            tool = self.brush_action.toggle()
        elif tool_id == ds.data.paint_tools.DRAG_DRAW:
            tool = self.drag_draw_action.toggle()
        elif tool_id == ds.data.paint_tools.DRAG:
            tool = self.drag_action.toggle()
        elif tool_id == ds.data.paint_tools.BUCKET:
            tool = self.bucket_action.toggle()
        elif tool_id == ds.data.paint_tools.ERASER:
            tool = self.eraser_action.toggle()
        elif tool_id == ds.data.paint_tools.DROPPER:
            tool = self.dropper_action.toggle()
        elif tool_id == ds.data.paint_tools.SELECT:
            tool = self.select_action.toggle()
        return tool

    def setToolSelection(self, state):
        tool = self.tool_group.checkedAction()
        if tool and state:
            tool_name = tool.text()
            self.icons.setCursorIconByTool(tool_name)
            ds.data.paint_tools.changeSelection(tool_name)
            print(ds.data.paint_tools.selection)
        else:
            print("No tools are currently selected.")
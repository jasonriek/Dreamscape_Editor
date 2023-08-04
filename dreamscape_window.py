from PySide6.QtWidgets import (QMainWindow, QToolBar, QWidget, QScrollArea, QMenu, QDockWidget, 
                               QCheckBox, QVBoxLayout, QSizePolicy, QDialog)
from PySide6.QtGui import (QAction, QIcon, QImage, QCursor, QPixmap, QActionGroup)
from PySide6.QtCore import (Qt, Signal, QRect, QSize)

from dreamscape_layers import (Layers)
from dreamscape_tiles import (TilesetBar, TileCanvas)
from dreamscape_tools import (Tools, ActiveTileWidget)
from dreamscape_dialogs import WorldSizeDialog

import dreamscape_config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        tileset_bar = TilesetBar()
        
        # Create and set up the TileCanvas dock
        scroll_area = QScrollArea(self)
        self.tile_canvas = TileCanvas(tileset_bar, scroll_area)

        # Create and set up the TileSelector dock
        tileset_selector_area = QWidget(self)
        tileset_selector_layout = QVBoxLayout(tileset_selector_area)
        tileset_selector_layout.setContentsMargins(0,0,0,0)
        self.tileset_selector_grid_checkbox = QCheckBox('Tileset Grid', self)
        self.tileset_selector_grid_checkbox.setChecked(False)
        self.tileset_selector_grid_checkbox.stateChanged.connect(tileset_bar.tile_selector.toggle_grid)
        tileset_bar.layout_.addWidget(self.tileset_selector_grid_checkbox)
        tileset_selector_layout.addWidget(tileset_bar)

        
        selector_dock = QDockWidget("Tile Selector", self)
        selector_dock.setWidget(tileset_selector_area)
        

        tileset_bar.tile_selector.active_tile_widget = ActiveTileWidget(self.tile_canvas)
        self.tile_canvas.tileDropperClicked.connect(tileset_bar.tile_selector.selectTile)
        
        layers_area = QWidget(self)
        layers_layout = QVBoxLayout(layers_area)
        layers_layout.setContentsMargins(0,0,0,0)
        layers_widget = Layers(self.tile_canvas)
        layers_widget.tilesetRemoved.connect(tileset_bar.removeTabByTilesetPath)
        layers_layout.addWidget(layers_widget)
        
        self.tile_canvas.layers_widget = layers_widget
        
        scroll_area.setWidget(self.tile_canvas)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        # Create and set up the ToolDock
        tool_dock = QDockWidget("Tools", self)
        tools = Tools(tileset_bar, self.tile_canvas, layers_widget)
        tools.addToLayout(tileset_bar.tile_selector.active_tile_widget)
        tools.setInternalWidgets()
        tool_dock.setWidget(tools)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, tool_dock)
        layers_dock = QDockWidget('Layers', self)
        layers_dock.setWidget(layers_area)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, selector_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, layers_dock)
        # Enable dock nesting
        self.setDockNestingEnabled(True)
        # Adjust the placement of canvas_dock and layers_dock
        # This line places layers_dock beside canvas_dock and sets the initial size ratio.
        self.setWindowTitle("Dreamscape Editor")
        self.setupTopMenu()
        self.setupToolBar()
        self.tile_canvas.tileDropperClicked.connect(self.pencil_action.toggle)
        self.setCentralWidget(scroll_area)

        tileset_bar.tile_selector.selectTile(0, 2)
        self.pencil_action.toggle()
        

    def _getToolIcon(self, x, y, w=64, h=64):
        clip_space = QRect(x, y, w, h)
        clipped = self.icons.copy(clip_space)
        icon = QIcon()
        icon.addPixmap(clipped)
        return icon
    
    def setToolCursorIcon(self, x, y, w=64, h=64):
        clip_space = QRect(x, y, w, h)
        clipped = self.icons.copy(clip_space)
        self.scaled_pix = clipped.scaled(QSize(20, 20), Qt.AspectRatioMode.KeepAspectRatio)
        self.current_cursor = QCursor(self.scaled_pix, -1, -1)
        self.tile_canvas.setCursor(self.current_cursor)

    def setCursorIconByTool(self, tool_name:str):
        if tool_name == 'Pencil':
            self.setToolCursorIcon(0, 0)
        elif tool_name == 'Brush':
            self.setToolCursorIcon(64*3, 0)
        elif tool_name == 'Drag & Draw':
            self.setToolCursorIcon(64, 0)
        elif tool_name == 'Drag':
            self.setToolCursorIcon(64*2, 0)
        elif tool_name == 'Bucket':
            self.setToolCursorIcon(64*5, 0)
        elif tool_name == 'Eraser':
            self.setToolCursorIcon(64*6, 0)
        elif tool_name == 'Dropper':
            self.setToolCursorIcon(64*4, 0)
        
    def setToolSelection(self, state):
        tool = self.tool_group.checkedAction()
        if tool and state:
            tool_name = tool.text()
            self.setCursorIconByTool(tool_name)
            dreamscape_config.paint_tools.changeSelection(tool_name)
            print(dreamscape_config.paint_tools.selection)
        else:
            print("No tools are currently selected.")

    def setupToolBar(self):
        self.icons = QPixmap('resources/paint_tool_icons.png')
        # Create the toolbar
        self.toolbar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Tile Pencil Brush
        self.pencil_action = QAction(self._getToolIcon(0, 0), 'Pencil', self)
        self.pencil_action.setCheckable(True)
        self.pencil_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.pencil_action)

        # Tile Paint Brush
        self.brush_action = QAction(self._getToolIcon(64*3, 0), 'Brush', self)
        self.brush_action.setCheckable(True)
        self.brush_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.brush_action)

        # Drag and Draw
        self.drag_draw_action = QAction(self._getToolIcon(64, 0), 'Drag & Draw', self)
        self.drag_draw_action.setCheckable(True)
        self.drag_draw_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.drag_draw_action)

        # Drag
        self.drag_action = QAction(self._getToolIcon(64*2, 0), 'Drag', self)
        self.drag_action.setCheckable(True)
        self.drag_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.drag_action)

        # Paint Bucket
        self.bucket_action = QAction(self._getToolIcon(64*5, 0), 'Bucket Fill', self)
        self.bucket_action.setCheckable(True)
        self.bucket_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.bucket_action)

        # Dropper
        self.dropper_action = QAction(self._getToolIcon(64*4, 0), 'Dropper', self)
        self.dropper_action.setCheckable(True)
        self.dropper_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.dropper_action)

        # Eraser
        self.eraser_action = QAction(self._getToolIcon(64*6, 0), 'Eraser', self)
        self.eraser_action.setCheckable(True)
        self.eraser_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.eraser_action)

        # Ensure only one toggle button can be active at a time
        self.tool_group = QActionGroup(self)
        self.tool_group.addAction(self.pencil_action)
        self.tool_group.addAction(self.brush_action)
        self.tool_group.addAction(self.drag_draw_action)
        self.tool_group.addAction(self.drag_action)
        self.tool_group.addAction(self.bucket_action)
        self.tool_group.addAction(self.dropper_action)
        self.tool_group.addAction(self.eraser_action)
        self.tool_group.setExclusive(True)

    def setupTopMenu(self):
        # Create the File menu
        self.menu_file = QMenu('File', self)
        self.action_exit = QAction('Exit', self)
        self.action_exit.triggered.connect(self.close)
        self.menu_file.addAction(self.action_exit)

        # Create the Edit menu
        self.menu_edit = QMenu('Edit', self)
        self.action_set_world_size = QAction('Set World Size', self)
        self.action_set_world_size.triggered.connect(self.setWorldSize)
        #self.action_set_world_size.triggered.connect(self.show_set_world_size_dialog)
        self.menu_edit.addAction(self.action_set_world_size)

        # Create the View menu
        self.menu_view = QMenu('View', self)
        self.action_world_grid = QAction('World grid')
        self.action_world_grid.setCheckable(True)
        self.action_world_grid.setChecked(True)
        self.action_world_grid.toggled.connect(self.tile_canvas.toggle_grid)
        self.menu_view.addAction(self.action_world_grid)


        # Add menus to the menu bar
        self.menuBar().addMenu(self.menu_file)
        self.menuBar().addMenu(self.menu_edit)
        self.menuBar().addMenu(self.menu_view)

        # ... (rest of your MainWindow initialization)

    def setWorldSize(self):
        dialog = WorldSizeDialog()
        ok = dialog.exec()
        if ok:
            w, h = dialog.get_values()
            dreamscape_config.tileset_layers.world_size_width = w
            dreamscape_config.tileset_layers.world_size_height = h
            self.tile_canvas.resize_canvas(dreamscape_config.tileset_layers.displayWidth(), dreamscape_config.tileset_layers.displayHeight())
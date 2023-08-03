from PySide6.QtWidgets import (QMainWindow, QToolBar, QWidget, QScrollArea, QMenu, QDockWidget, 
                               QCheckBox, QVBoxLayout, QSizePolicy, QDialog)
from PySide6.QtGui import (QAction, QIcon, QImage, QPixmap, QActionGroup)
from PySide6.QtCore import (Qt, Signal, QRect)

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
        self.tile_canvas = TileCanvas(tileset_bar)

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
        
        layers_area = QWidget(self)
        layers_layout = QVBoxLayout(layers_area)
        layers_layout.setContentsMargins(0,0,0,0)
        layers_widget = Layers(self.tile_canvas)
        self.tile_grid_checkbox = QCheckBox('World Grid', self)
        self.tile_grid_checkbox.setChecked(True)
        layers_layout.addWidget(layers_widget)
        layers_layout.addWidget(self.tile_grid_checkbox)
        
        self.tile_canvas.layers_widget = layers_widget
        self.tile_grid_checkbox.stateChanged.connect(self.tile_canvas.toggle_grid)
        scroll_area = QScrollArea()
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
        self.setCentralWidget(scroll_area)

    def _getToolIcon(self, x, y, icons:QPixmap=None, w=64, h=64):
        clip_space = QRect(x, y, w, h)
        clipped = icons.copy(clip_space)
        icon = QIcon()
        icon.addPixmap(clipped)
        return icon

    def setupToolBar(self):
        self.icons = QPixmap('resources/paint_tool_icons.png')
        # Create the toolbar
        self.toolbar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Tile Paint Brush
        self.brush_action = QAction(self._getToolIcon(64*3, 0, self.icons), 'Brush', self)
        self.brush_action.setCheckable(True)
        self.toolbar.addAction(self.brush_action)

        # Eraser
        self.eraser_action = QAction(self._getToolIcon(64*6, 0, self.icons), 'Eraser', self)
        self.eraser_action.setCheckable(True)
        self.toolbar.addAction(self.eraser_action)

        # Drag and Draw
        self.drag_draw_action = QAction(self._getToolIcon(64, 0, self.icons), 'Drag & Draw', self)
        self.drag_draw_action.setCheckable(True)
        self.toolbar.addAction(self.drag_draw_action)

        # Paint Bucket
        self.bucket_action = QAction(self._getToolIcon(64*5, 0, self.icons), 'Bucket Fill', self)
        self.bucket_action.setCheckable(True)
        self.toolbar.addAction(self.bucket_action)

        # Dropper
        self.dropper_action = QAction(self._getToolIcon(64*4, 0, self.icons), 'Dropper', self)
        self.dropper_action.setCheckable(True)
        self.toolbar.addAction(self.dropper_action)

        # Ensure only one toggle button can be active at a time
        self.tool_group = QActionGroup(self)
        self.tool_group.addAction(self.brush_action)
        self.tool_group.addAction(self.eraser_action)
        self.tool_group.addAction(self.drag_draw_action)
        self.tool_group.addAction(self.bucket_action)
        self.tool_group.addAction(self.dropper_action)
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

        # Add menus to the menu bar
        self.menuBar().addMenu(self.menu_file)
        self.menuBar().addMenu(self.menu_edit)

        # ... (rest of your MainWindow initialization)

    def setWorldSize(self):
        dialog = WorldSizeDialog()
        ok = dialog.exec()
        if ok:
            w, h = dialog.get_values()
            dreamscape_config.tileset_layers.world_size_width = w
            dreamscape_config.tileset_layers.world_size_height = h
            self.tile_canvas.resize_canvas(dreamscape_config.tileset_layers.displayWidth(), dreamscape_config.tileset_layers.displayHeight())
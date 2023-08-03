from PySide6.QtWidgets import (QMainWindow, QWidget, QScrollArea, QMenu, QDockWidget, 
                               QCheckBox, QVBoxLayout, QSizePolicy, QDialog)
from PySide6.QtGui import (QAction)
from PySide6.QtCore import (Qt, Signal)

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
        self.setCentralWidget(scroll_area)


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
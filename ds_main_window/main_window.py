from PySide6.QtWidgets import (QMainWindow, QWidget, QScrollArea, QDockWidget, QCheckBox, QVBoxLayout, QHBoxLayout, QSizePolicy)
from PySide6.QtCore import (Qt)

from ds_layers import (Layers)
from ds_tiles import (TileCanvas, TilesetTabBar)
from ds_tools import (TilesetProperties, ActiveTileWidget)

from .icons import Icons
from .top_menu import TopMenu
from .toolbar import Toolbar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tileset_tab_bar = TilesetTabBar()
        self.tile_canvas_scroll_area = QScrollArea(self)
        self.tile_canvas = TileCanvas(self.tileset_tab_bar, self.tile_canvas_scroll_area)
        self.active_tile_widget = ActiveTileWidget(self.tile_canvas)
        self.layers = Layers(self.tile_canvas)
        self.tileset_properties = TilesetProperties(self.tileset_tab_bar, self.tile_canvas, self.layers)
        self.icons = Icons(self)

        self.setupTileCanvas()
        self.setupTilesetTabBar()
        self.setupLayers()
        self.setupTilesetSelectorCheckbox()

        self.top_menu = TopMenu(self)
        self.toolbar = Toolbar(self)

        self.initUI()
        self.setupDocks()

        self.top_menu.setup()
        self.toolbar.setup()

        self.tile_canvas.undoClicked.connect(self.top_menu.enableUndo)
        self.tile_canvas.redoClicked.connect(self.top_menu.enableRedo)
        self.tile_canvas.initUndo.connect(self.top_menu.enableUndo)
        self.tileset_tab_bar.tile_selector.selectTile(0, 2)
        self.toolbar.select_action.toggle()
        self.tile_canvas.tileDropperReleased.connect(self.toolbar.tool)

        self.setStatusBar(self.tileset_properties.status_bar)

    def setupTileCanvas(self):
        self.tile_canvas.tileDropperClicked.connect(self.tileset_tab_bar.tile_selector.selectTileFromDropper)
        self.tile_canvas.tileDropperClicked.connect(self.icons.setDropperIcon)

    def setupTilesetTabBar(self):
        self.tileset_tab_bar.tile_selector.active_tile_widget = self.active_tile_widget
        self.tileset_tab_bar.tile_selector.active_tile_widget.collision_checkbox.clicked.connect(self.tile_canvas.setTileCollision)
        self.tileset_tab_bar.tile_selector.active_tile_widget.overlay_checkbox.clicked.connect(self.tile_canvas.setTileOverlay)
        self.tileset_tab_bar.tile_selector.active_tile_widget.worldTileClicked.connect(self.tileset_tab_bar.tile_selector.selectTile)
        self.tile_canvas.tileSelected.connect(self.tileset_tab_bar.tile_selector.active_tile_widget.updateTileProperties)
    
    def setupLayers(self):        
        self.layers.tilesetRemoved.connect(self.tileset_tab_bar.removeTabByTilesetPath)    
        self.tile_canvas.layers = self.layers
    
    def setupTilesetSelectorCheckbox(self):
        self.tileset_selector_grid_checkbox = QCheckBox('Tileset Grid', self)
        self.tileset_selector_grid_checkbox.setChecked(False)
        self.tileset_selector_grid_checkbox.stateChanged.connect(self.tileset_tab_bar.tile_selector.toggleGrid)

    def initUI(self):
        self.setWindowTitle("Dreamscape Editor")

        # Tileset Selector
        self.tileset_selector_area = QWidget(self)
        self.tileset_selector_layout = QVBoxLayout(self.tileset_selector_area)
        self.tileset_selector_layout.setContentsMargins(3,0,6,0)

        # Tileset Selector Top Area
        self.tileset_selector_top_area = QWidget(self)
        self.tileset_selector_top_layout = QHBoxLayout(self.tileset_selector_top_area)
        self.tileset_selector_top_layout.setContentsMargins(0,0,0,0)

        self.tileset_selector_bottom_area = QWidget(self)
        self.tileset_selector_bottom_layout = QHBoxLayout(self.tileset_selector_bottom_area)
        self.tileset_selector_bottom_layout.setContentsMargins(0,0,0,0)
        self.tileset_selector_bottom_layout.addWidget(self.tileset_selector_grid_checkbox)
        self.tileset_selector_bottom_layout.addWidget(self.tileset_properties.tileset_coord_label)

        self.tileset_tab_bar._layout.addWidget(self.tileset_selector_bottom_area)
        self.tileset_selector_layout.addWidget(self.tileset_properties.tileset_loader)
        self.tileset_selector_layout.addWidget(self.tileset_selector_top_area)
        self.tileset_selector_layout.addWidget(self.tileset_tab_bar)

        
        self.tileset_selector_top_layout.addWidget(self.tileset_tab_bar.tile_selector.active_tile_widget)

        # Layers
        self.layers_area = QWidget(self)
        self.layers_layout = QVBoxLayout(self.layers_area)
        self.layers_layout.setContentsMargins(0,0,0,0)
        self.layers_layout.addWidget(self.layers)

        self.tile_canvas_scroll_area.setWidget(self.tile_canvas)
        self.tile_canvas_scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.tile_canvas_scroll_area)

    def setupDocks(self):
        # Create and set up the TileCanvas dock
        self.selector_dock = QDockWidget("Tile Selector", self)

        self.selector_dock.setWidget(self.tileset_selector_area)

        self.layers_dock = QDockWidget('Layers', self)
        self.layers_dock.setWidget(self.layers_area)
        
        # Add docks
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.selector_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layers_dock)
        
        
        
          

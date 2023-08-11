from PySide6.QtWidgets import (QMainWindow, QToolBar, QWidget, QScrollArea, QMenu, QDockWidget, 
                               QCheckBox, QVBoxLayout, QSizePolicy, QFileDialog)
from PySide6.QtGui import (QAction, QIcon, QKeySequence, QCursor, QPixmap, QActionGroup)
from PySide6.QtCore import (Qt, QRect, QSize)

from dreamscape_layers import (Layers)
from dreamscape_tiles import (TilesetBar, TileCanvas)
from dreamscape_tools import (Tools, ActiveTileWidget)
from dreamscape_dialogs import WorldSizeDialog

import dreamscape_config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tileset_bar = TilesetBar()
        
        # Create and set up the TileCanvas dock
        scroll_area = QScrollArea(self)
        self.tile_canvas = TileCanvas(self.tileset_bar, scroll_area)
        self.tile_canvas.undoClicked.connect(self.enableUndo)
        self.tile_canvas.redoClicked.connect(self.enableRedo)
        self.tile_canvas.initUndo.connect(self.enableUndo)

        # Create and set up the TileSelector dock
        tileset_selector_area = QWidget(self)
        tileset_selector_layout = QVBoxLayout(tileset_selector_area)
        tileset_selector_layout.setContentsMargins(0,0,0,0)
        self.tileset_selector_grid_checkbox = QCheckBox('Tileset Grid', self)
        self.tileset_selector_grid_checkbox.setChecked(False)
        self.tileset_selector_grid_checkbox.stateChanged.connect(self.tileset_bar.tile_selector.toggle_grid)
        self.tileset_bar.layout_.addWidget(self.tileset_selector_grid_checkbox)
        tileset_selector_layout.addWidget(self.tileset_bar)

        
        selector_dock = QDockWidget("Tile Selector", self)
        selector_dock.setWidget(tileset_selector_area)
        
        
        self.tileset_bar.tile_selector.active_tile_widget = ActiveTileWidget(self.tile_canvas)
        self.tileset_bar.tile_selector.active_tile_widget.collision_checkbox.stateChanged.connect(self.tile_canvas.setTileCollision)
        self.tileset_bar.tile_selector.active_tile_widget.overlay_checkbox.stateChanged.connect(self.tile_canvas.setTileOverlay)
        self.tileset_bar.tile_selector.active_tile_widget.worldTileClicked.connect(self.tileset_bar.tile_selector.selectTile)
        self.tile_canvas.tileDropperClicked.connect(self.tileset_bar.tile_selector.selectTileFromDropper)
        self.tile_canvas.tileDropperClicked.connect(self.setDropperIcon)
        self.tile_canvas.tileSelected.connect(self.tileset_bar.tile_selector.active_tile_widget.updateTileProperties)

        layers_area = QWidget(self)
        layers_layout = QVBoxLayout(layers_area)
        layers_layout.setContentsMargins(0,0,0,0)
        self.layers_widget = Layers(self.tile_canvas)
        self.layers_widget.tilesetRemoved.connect(self.tileset_bar.removeTabByTilesetPath)
        layers_layout.addWidget(self.layers_widget)
        
        self.tile_canvas.layers_widget = self.layers_widget
        
        scroll_area.setWidget(self.tile_canvas)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        # Create and set up the ToolDock
        tool_dock = QDockWidget("Tools", self)
        tools = Tools(self.tileset_bar, self.tile_canvas, self.layers_widget)
        

        tools.addToLayout(self.tileset_bar.tile_selector.active_tile_widget)
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

        self.tileset_bar.tile_selector.selectTile(0, 2)
        self.select_action.toggle()
        self.tile_canvas.tileDropperReleased.connect(self.getTool)
        

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

    def setDropperIcon(self):
        self.setToolCursorIcon(64*4, 0)

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

    def getTool(self):
        tool_id = dreamscape_config.paint_tools.selection
        tool = self.pencil_action.toggle()   
        if tool_id == dreamscape_config.PENCIL:
            tool = self.pencil_action.toggle()
        elif tool_id == dreamscape_config.BRUSH:
            tool = self.brush_action.toggle()
        elif tool_id == dreamscape_config.DRAG_DRAW:
            tool = self.drag_draw_action.toggle()
        elif tool_id == dreamscape_config.DRAG:
            tool = self.drag_action.toggle()
        elif tool_id == dreamscape_config.BUCKET:
            tool = self.bucket_action.toggle()
        elif tool_id == dreamscape_config.ERASER:
            tool = self.eraser_action.toggle()
        elif tool_id == dreamscape_config.DROPPER:
            tool = self.dropper_action.toggle()
        elif tool_id == dreamscape_config.SELECT:
            tool = self.select_action.toggle()
        return tool
          
    def setToolSelection(self, state):
        tool = self.tool_group.checkedAction()
        if tool and state:
            tool_name = tool.text()
            self.setCursorIconByTool(tool_name)
            dreamscape_config.paint_tools.changeSelection(tool_name)
            print(dreamscape_config.paint_tools.selection)
        else:
            print("No tools are currently selected.")
    
    def defaultMouseIcon(self):
        clip_space = QRect(0, 0, 32, 6432)
        clipped = self.mouse_icon.copy(clip_space)
        scaled = clipped.scaled(QSize(20, 20), Qt.AspectRatioMode.KeepAspectRatio)
        icon = QIcon()
        icon.addPixmap(scaled)
        return icon

    def setDefaultCursor(self):
        self.tile_canvas.setCursor(Qt.CursorShape.ArrowCursor)

    def setupToolBar(self):
        self.icons = QPixmap('resources/paint_tool_icons.png')
        self.mouse_icon = QPixmap('resources/mouse.png')
        # Create the toolbar
        self.toolbar = QToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # Select Mode
        self.select_action = QAction(self.defaultMouseIcon(), 'Select', self)
        self.select_action.setCheckable(True)
        self.select_action.toggled.connect(self.setToolSelection)
        self.toolbar.addAction(self.select_action)

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
        self.tool_group.addAction(self.select_action)
        self.tool_group.addAction(self.pencil_action)
        self.tool_group.addAction(self.brush_action)
        self.tool_group.addAction(self.drag_draw_action)
        self.tool_group.addAction(self.drag_action)
        self.tool_group.addAction(self.bucket_action)
        self.tool_group.addAction(self.dropper_action)
        self.tool_group.addAction(self.eraser_action)
        self.tool_group.setExclusive(True)

    def enableUndo(self, enable:bool):
        self.undo_action.setEnabled(enable)
    
    def enableRedo(self, enable:bool):
        self.redo_action.setEnabled(enable)

    def setupTopMenu(self):
        # Create the File menu
        self.menu_file = QMenu('File', self)

        # Open action
        self.action_open = QAction('Open', self)
        self.action_open.triggered.connect(self.openFile)
        self.menu_file.addAction(self.action_open)

        # Save action
        self.action_save = QAction('Save', self)
        self.action_save.triggered.connect(self.saveFile)
        self.menu_file.addAction(self.action_save)

        # Save As action
        self.action_save_as = QAction('Save As', self)
        self.action_save_as.triggered.connect(self.saveFileAs)
        self.menu_file.addAction(self.action_save_as)

        self.menu_file.addSeparator()
        self.action_exit = QAction('Exit', self)
        self.action_exit.triggered.connect(self.close)
        self.menu_file.addAction(self.action_exit)

        self.menu_edit = QMenu('Edit', self)
        
        # Create the Edit menu
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.tile_canvas.undo)
        self.menu_edit.addAction(self.undo_action)

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.tile_canvas.redo)
        self.menu_edit.addAction(self.redo_action)

        self.menu_edit.addSeparator()

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

        self.action_show_tile_collisions = QAction('Tile Collisions')
        self.action_show_tile_collisions.setCheckable(True)
        self.action_show_tile_collisions.setChecked(True)
        self.action_show_tile_collisions.toggled.connect(self.tile_canvas.toggleShowTileCollisons)
        self.menu_view.addAction(self.action_show_tile_collisions)

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

    def openFile(self):
        # Show an Open File dialog and get the selected file path
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Tileset Files (*.ts);;All Files (*)")
        
        if file_path:
            # Logic to load the file data and update the TileCanvas
            dreamscape_config.tileset_layers = dreamscape_config.loadFromFile(file_path)
            tilesets = []
            self.layers_widget.clear()
            for i in range(self.tileset_bar.tab_bar.count()):
                self.tileset_bar.tab_bar.removeTab(i)
            for layer_name in dreamscape_config.tileset_layers.order:
                tileset = dreamscape_config.tileset_layers.layers[layer_name]['tileset']
                self.layers_widget.addLayer(dreamscape_config.tileset_layers.layers[layer_name]['name'], tileset, False)
                if tileset not in tilesets:
                    tilesets.append(tileset)
                    self.tileset_bar.addTileset(dreamscape_config.tileset_layers.layers[layer_name]['name'], tileset)

            self.tile_canvas.update()
            self.tile_canvas.redraw_world()
                


    def saveFile(self):
        # Logic to save the current data
        # If there's already an existing path, save to it. Otherwise, show the Save As dialog.
        pass

    def saveFileAs(self):
        # Show a Save File As dialog and get the selected file path
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Tileset Files (*.ts);;All Files (*)")
        
        if file_path:
            # Logic to save the current data to the selected file
            dreamscape_config.saveToFile(dreamscape_config.tileset_layers, file_path)
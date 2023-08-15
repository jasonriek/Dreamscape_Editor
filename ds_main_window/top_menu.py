from PySide6.QtWidgets import (QMenu, QFileDialog)
from PySide6.QtGui import (QAction,QKeySequence)

from ds_dialogs import WorldSizeDialog

import ds


class TopMenu:
    def __init__(self, main_window):
        self.main_window = main_window

    def setup(self):
        # Create the File menu
        self.menu_file = QMenu('File', self.main_window)

        # Open action
        self.action_open = QAction('Open')
        self.action_open.triggered.connect(self.openFile)
        self.menu_file.addAction(self.action_open)

        # Save action
        self.action_save = QAction('Save')
        self.action_save.triggered.connect(self.saveFile)
        self.menu_file.addAction(self.action_save)

        # Save As action
        self.action_save_as = QAction('Save As')
        self.action_save_as.triggered.connect(self.saveFileAs)
        self.menu_file.addAction(self.action_save_as)
        self.menu_file.addSeparator()
        # Export World Action
        self.action_export_world = QAction('Export World')
        self.action_export_world.triggered.connect(self.exportJSON)
        self.menu_file.addAction(self.action_export_world)

        self.menu_file.addSeparator()
        self.action_exit = QAction('Exit')
        self.action_exit.triggered.connect(self.main_window.close)
        self.menu_file.addAction(self.action_exit)

        self.menu_edit = QMenu('Edit')
        # Create the Edit menu
        self.undo_action = QAction('Undo')
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.main_window.tile_canvas.undo)
        self.menu_edit.addAction(self.undo_action)

        self.redo_action = QAction('Redo')
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.main_window.tile_canvas.redo)
        self.menu_edit.addAction(self.redo_action)

        self.menu_edit.addSeparator()

        self.action_set_world_size = QAction('Set World Size')
        self.action_set_world_size.triggered.connect(self.setWorldSize)
        self.menu_edit.addAction(self.action_set_world_size)

        # Create the View menu
        self.menu_view = QMenu('View')
        self.action_world_grid = QAction('World grid')
        self.action_world_grid.setCheckable(True)
        self.action_world_grid.setChecked(True)
        self.action_world_grid.toggled.connect(self.main_window.tile_canvas.toggleGrid)
        self.menu_view.addAction(self.action_world_grid)

        self.action_show_tile_collisions = QAction('Tile Collisions')
        self.action_show_tile_collisions.setCheckable(True)
        self.action_show_tile_collisions.setChecked(True)
        self.action_show_tile_collisions.toggled.connect(self.main_window.tile_canvas.toggleShowTileCollisons)
        self.menu_view.addAction(self.action_show_tile_collisions)

        # Add menus to the menu bar
        self.main_window.menuBar().addMenu(self.menu_file)
        self.main_window.menuBar().addMenu(self.menu_edit)
        self.main_window.menuBar().addMenu(self.menu_view)

    def enableUndo(self, enable:bool):
        self.undo_action.setEnabled(enable)
    
    def enableRedo(self, enable:bool):
        self.redo_action.setEnabled(enable)

    def setWorldSize(self):
        dialog = WorldSizeDialog()
        ok = dialog.exec()
        if ok:
            w, h = dialog.get_values()
            ds.data.world.setWidth(w)
            ds.data.world.setHeight(h)
            self.main_window.tile_canvas.resizeCanvas(ds.data.world.displayWidth(), ds.data.world.displayHeight())

    def openFile(self):
        # Show an Open File dialog and get the selected file path
        file_path, _ = QFileDialog.getOpenFileName(self.main_window, "Open File", "", "Tileset Files (*.ts);;All Files (*)")
        
        if file_path:
            # Logic to load the file data and update the TileCanvas
            ds.data = ds.Utils.loadFromFile(file_path)
            tilesets = []
            self.main_window.layers.clear()
            for i in range(self.main_window.tileset_tab_bar.tab_bar.count()):
                self.main_window.tileset_tab_bar.tab_bar.removeTab(i)
            for layer_name in ds.data.layers.order:
                tileset = ds.data.layers[layer_name]['tileset']
                self.main_window.layers.addLayer(ds.data.layers[layer_name]['name'], tileset, False)
                if tileset not in tilesets:
                    tilesets.append(tileset)
                    self.main_window.tileset_tab_bar.addTileset(ds.data.layers[layer_name]['name'], tileset)

            self.main_window.tile_canvas.update()
            self.main_window.tile_canvas.redrawWorld()
                
    def saveFile(self):
        # Logic to save the current data
        # If there's already an existing path, save to it. Otherwise, show the Save As dialog.
        pass

    def saveFileAs(self):
        # Show a Save File As dialog and get the selected file path
        file_path, _ = QFileDialog.getSaveFileName(self.main_window, "Save File As", "", "Tileset Files (*.ts);;All Files (*)")
        
        if file_path:
            # Logic to save the current data to the selected file
            ds.Utils.saveToFile(ds.data, file_path)
    
    def exportJSON(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(self.main_window, "Export World JSON", "", "JSON Files (*.json)")
            if file_path:
                overlay_file_path = file_path.split('.')[0] + '_overlay.json'
                with open(file_path, 'w') as f, open(overlay_file_path, 'w') as fo:
                    game, game_overlay = ds.data.layers.getJson()
                    f.write(game)
                    fo.write(game_overlay)
        except Exception as error:
            print(f'exportJSON() Error: {str(error)}')
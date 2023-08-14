from PySide6.QtWidgets import (QAbstractItemView, QSizePolicy, QVBoxLayout, QWidget, QListView, QMenu, QInputDialog, QMessageBox)
from PySide6.QtGui import (QAction, QPixmap)
from PySide6.QtCore import (Signal, Qt, QModelIndex)

from .layer_list_model import LayerListModel

import ds


class Layers(QWidget):
    layerClicked = Signal(str)
    tilesetRemoved = Signal(str)
    def __init__(self, tile_canvas):
        super().__init__()
        self.tile_canvas = tile_canvas
        # Create a QVBoxLayout for this widget
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.view = QListView(self)
        self.view.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.model = LayerListModel()
        self.view.setModel(self.model)
        self.view.setAlternatingRowColors(True)
        self.view.setDragEnabled(True)
        self.view.setAcceptDrops(True)
        self.view.setDropIndicatorShown(True)
        self.view.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.view.selectionModel().currentChanged.connect(self.layerChanged)
        self.model.swapped.connect(self.layerSwapped)
         # Set the custom context menu for the QListView
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.showContextMenu)
        self.model.dataChanged.connect(self.view.update)
        self.view.setMinimumWidth(250)
        layout.addWidget(self.view)
        self.view.selectionModel().currentChanged.connect(self.clickLayer)

        # Create sample layers for this example
        for i in range(ds.data.layers.length()):
            layer = {'name': f"[Layer {i+1}]   {ds.data.layers.getLayerNameByIndex(i)}"}
            self.model.addLayer(layer)

    def clickLayer(self, current_index:QModelIndex, previous_index:QModelIndex):
        layer_path = ds.data.layers.getPathByLayerName(ds.data.layers.active_layer_name)
        self.layerClicked.emit(layer_path)

    def layerChanged(self, current, previous):
        ds.data.layers.active_layer_name = ds.data.layers.getLayerNameByIndex(current.row())

    def layerSwapped(self, row1, row2):
        self.tile_canvas.swapLayers(row1, row2)

    def selectedLayerIndex(self):
        return self.view.selectionModel().currentIndex().row()
    
    def updateVisibility(self, state):
        row = ds.data.layers.getActiveLayerIndex()
        hidden_label = ''
        if not state:
            if row is not None:
                hidden_label = '(Hidden)'
                
        data = {'name': f'[Layer {row + 1}]   {ds.data.layers.active_layer_name} {hidden_label}'}
        self.model.layers[row] = data
     
        ds.data.layers.changeVisibility(state)
        self.tile_canvas.update()
        self.tile_canvas.redrawWorld()

    # New method to display the context menu
    def showContextMenu(self, position):
        # Create a new QMenu
        context_menu = QMenu(self.view)
        
        # Get the name of the selected layer
        index = self.view.indexAt(position)
        if index.isValid():
            selected_layer = self.model.data(index, Qt.ItemDataRole.DisplayRole)
            layer_action = QAction(selected_layer, self.view)
            layer_action.setEnabled(False)  # Set it to disabled, so it's just for display
            context_menu.addAction(layer_action)
            context_menu.addSeparator()  # Add a line separator
            visible_action = QAction('Visible', self.view)
            visible_action.setCheckable(True)
            visible_action.setChecked(ds.data.layers.layer_visibility[index.row()])
            visible_action.toggled.connect(self.updateVisibility)
            context_menu.addAction(visible_action)
            context_menu.addSeparator()
        
        # Add the add layer and remove layer actions
        add_layer_action = QAction("Add Layer", self.view)
        add_layer_action.triggered.connect(self.addNewLayer)
        context_menu.addAction(add_layer_action)

        if index.isValid():  # Only add the remove action if a valid layer is clicked
            remove_layer_action = QAction("Remove Layer", self.view)
            remove_layer_action.triggered.connect(self.remove_selected_layer)
            context_menu.addAction(remove_layer_action)
        
        # Show the context menu
        context_menu.exec(self.view.viewport().mapToGlobal(position))
    
    def addLayer(self, name:str, path:str, create_pixmaps=True):
        if not ds.data.layers.setting_tileset:
            ds.data.layers.appendTilesetLayer(name, path, 32, 32)

            if create_pixmaps:
                ds.data.layers.pixmaps.append(QPixmap(ds.data.world.displayWidth(), ds.data.world.displayHeight()))
        else:
            ds.data.layers.setting_tileset = False
        row = self.model.rowCount()
        new_layer = {'name': f"[Layer {row + 1}]   {name}"}
        self.model.addLayer(new_layer)
        index = self.model.index(self.model.rowCount() - 1, 0)
        self.view.setCurrentIndex(index)
        self.tile_canvas.update()
        self.tile_canvas.redrawWorld()

    def selectFistLayerWithTilesetPath(self, path):
        i = ds.data.layers.indexOfFirstTilesetWithPath(path)
        index = self.model.index(i, 0)
        self.view.setCurrentIndex(index)
        self.tile_canvas.update()
        self.tile_canvas.redrawWorld()

    # New method to handle adding a new layer from the context menu
    def addNewLayer(self):
        layer_name, ok = QInputDialog.getText(self, "New Layer", "Enter name for the new layer:")
        # Check if the user clicked OK and provided a name.
        while not layer_name.strip() and ok:
            QMessageBox.warning(self, 'Empty Entry', 'Layer name cannot be empty.')
            layer_name, ok = QInputDialog.getText(self, "New Layer", "Enter name for the new layer:")
            
        if ok and layer_name:
            if ds.data.layers.layerNameExists(layer_name):
                QMessageBox.warning(self, 'Name Already Exists', f'Layer name "{layer_name}" already exists.')
            else:
                self.addLayer(layer_name, ds.data.layers.active_layer_src)

    def clear(self):
        self.model.beginRemoveRows(QModelIndex(), 0, self.model.rowCount() - 1)
        self.model.layers.clear()
        self.model.endRemoveRows()

    # New method to handle removing the selected layer from the context menu
    def remove_selected_layer(self):
        current_index = self.selectedLayerIndex()
        if ds.data.layers.length() == 1:
            QMessageBox.warning(self, 'Cannot Remove Layer', 'There must be at least one layer in the editor.')
            return
        
        if current_index != -1:  # Ensure a layer is selected
            layer_name = ds.data.layers.active_layer_name
            layer_path = ds.data.layers.active_layer_src
            button = QMessageBox.warning(self, 'Remove Layer', f'Are you sure you want to remove layer "{layer_name}"?', QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if button == QMessageBox.StandardButton.Ok:
                if(ds.data.layers.lastTileset(layer_path)):
                    button = QMessageBox.warning(self, 'Last Tileset Layer', f'This Layer is associated with a tileset, and will remove the "{layer_name}" tileset from the world.', QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                    if(button == QMessageBox.StandardButton.Ok):
                        ds.data.layers.removeTilesetLayerAtIndex(current_index)
                        self.tilesetRemoved.emit(layer_path)
                    else:
                        return
                self.model.beginRemoveRows(QModelIndex(), current_index, current_index)
                del self.model.layers[current_index]
                ds.data.layers.removeTilesetLayerAtIndex(current_index)
                self.model.endRemoveRows()
                index = self.model.index(0, 0)
                self.view.setCurrentIndex(index)
                self.tile_canvas.update()
                self.tile_canvas.redrawWorld()
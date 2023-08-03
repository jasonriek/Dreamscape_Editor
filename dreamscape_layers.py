from PySide6.QtWidgets import (QAbstractItemView, QSizePolicy, QVBoxLayout, QWidget, QListView, QMenu, QInputDialog, QMessageBox)
from PySide6.QtGui import (QAction, QPixmap)
from PySide6.QtCore import (QAbstractListModel, Signal, Qt, QModelIndex, QMimeData, QByteArray,
                            QDataStream, QIODevice)
import dreamscape_config

class LayerListModel(QAbstractListModel):
    swapped = Signal(int, int)
    
    def __init__(self, layers=None):
        super().__init__()
        if layers is None:
            layers = []
        self.layers = layers
        

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.layers[index.row()]['name']
        return None

    def setData(self, row:int, value, role=Qt.ItemDataRole.EditRole):
        index = self.index(row, 0)
        if not index.isValid():
            return False
        return super(LayerListModel, self).setData(index, value, role)

    def flags(self, index):
        default_flags = super().flags(index)
        return default_flags | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled

    def rowCount(self, index=QModelIndex()):
        return len(self.layers)

    def addLayer(self, layer):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.layers.append(layer)
        self.endInsertRows()
    
    def createLayerLabel(self, layer_name, old_layer_index, new_layer_index):
        hidden_label = '(Hidden)'
        visibility = dreamscape_config.tileset_layers.layer_visibility[old_layer_index]
        if visibility:
            hidden_label = '' 
        return {'name': f'Layer {new_layer_index + 1} ({layer_name}) {hidden_label}'}

    def swapRows(self, row1, row2):
        if 0 <= row1 < self.rowCount() and 0 <= row2 < self.rowCount():
            layer_1_name = dreamscape_config.tileset_layers.getLayerNameByIndex(row2)
            layer_2_name = dreamscape_config.tileset_layers.getLayerNameByIndex(row1)
            layer_1 = self.createLayerLabel(layer_1_name, row2, row1)
            layer_2 = self.createLayerLabel(layer_2_name, row1, row2)
            self.layers[row1] = layer_1
            self.layers[row2] = layer_2
            self.dataChanged.emit(self.index(row1, 0), self.index(row1, 0))
            self.dataChanged.emit(self.index(row2, 0), self.index(row2, 0))
            self.swapped.emit(row1, row2)

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def mimeTypes(self):
        return ["application/vnd.row.list"]

    def mimeData(self, indexes):
        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.OpenModeFlag.WriteOnly)
        for index in indexes:
            stream.writeInt32(index.row())
        mime_data.setData("application/vnd.row.list", encoded_data)
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        if not data.hasFormat("application/vnd.row.list"):
            return False
        if action == Qt.DropAction.IgnoreAction:
            return True
        if not parent.isValid():
            return False
        # Extract the row we want to move
        encoded_data = data.data("application/vnd.row.list")
        stream = QDataStream(encoded_data, QIODevice.OpenModeFlag.ReadOnly)
        rows_to_move = []
        while not stream.atEnd():
            row_to_move = stream.readInt32()
            rows_to_move.append(row_to_move)
        # Currently, only support moving one row
        row_to_move = rows_to_move[0]
        self.swapRows(row_to_move, parent.row())
        return True

class Layers(QWidget):
    layerClicked = Signal(str)
    def __init__(self, canvas):
        super().__init__()
        self.tile_canvas = canvas
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
        self.view.selectionModel().currentChanged.connect(self.layer_changed)
        self.model.swapped.connect(self.layer_swapped)
         # Set the custom context menu for the QListView
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)
        self.model.dataChanged.connect(self.view.update)
        self.view.setMinimumWidth(250)
        layout.addWidget(self.view)
        self.view.selectionModel().currentChanged.connect(self.clickLayer)

        # Create sample layers for this example
        for i in range(dreamscape_config.tileset_layers.length()):
            layer = {'name': f"Layer {i+1} ({dreamscape_config.tileset_layers.getLayerNameByIndex(i)})"}
            self.model.addLayer(layer)

    def clickLayer(self, current_index:QModelIndex, previous_index:QModelIndex):
        layer_path = dreamscape_config.tileset_layers.getPathByLayerName(dreamscape_config.tileset_layers.active_layer_name)
        self.layerClicked.emit(layer_path)

    def layer_changed(self, current, previous):
        dreamscape_config.tileset_layers.active_layer_name = dreamscape_config.tileset_layers.getLayerNameByIndex(current.row())

    def layer_swapped(self, row1, row2):
        self.tile_canvas.swap_layers(row1, row2)

    def get_selected_layer_index(self):
        return self.view.selectionModel().currentIndex().row()
    
    def updateVisibility(self, state):
        row = dreamscape_config.tileset_layers.getActiveLayerIndex()
        hidden_label = ''
        if not state:
            if row is not None:
                hidden_label = '(Hidden)'
                
        data = {'name': f'Layer {row + 1} ({dreamscape_config.tileset_layers.active_layer_name}) {hidden_label}'}
        self.model.layers[row] = data
     
        dreamscape_config.tileset_layers.changeVisibility(state)
        self.tile_canvas.update()
        self.tile_canvas.redraw_world()

    # New method to display the context menu
    def show_context_menu(self, position):
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
            visible_action.setChecked(dreamscape_config.tileset_layers.layer_visibility[index.row()])
            visible_action.toggled.connect(self.updateVisibility)
            context_menu.addAction(visible_action)
            context_menu.addSeparator()
        
        # Add the add layer and remove layer actions
        add_layer_action = QAction("Add Layer", self.view)
        add_layer_action.triggered.connect(self.add_new_layer)
        context_menu.addAction(add_layer_action)

        if index.isValid():  # Only add the remove action if a valid layer is clicked
            remove_layer_action = QAction("Remove Layer", self.view)
            remove_layer_action.triggered.connect(self.remove_selected_layer)
            context_menu.addAction(remove_layer_action)
        
        # Show the context menu
        context_menu.exec(self.view.viewport().mapToGlobal(position))
    
    def addLayer(self, name:str, path:str):
        dreamscape_config.tileset_layers.appendTilesetLayer(name, path, 32, 32)
        dreamscape_config.tileset_layers.layer_pixmaps.append(QPixmap(dreamscape_config.tileset_layers.displayWidth(), dreamscape_config.tileset_layers.displayHeight()))
        row = self.model.rowCount()
        new_layer = {'name': f"Layer {row + 1} ({name})"}
        self.model.addLayer(new_layer)
        index = self.model.index(self.model.rowCount() - 1, 0)
        self.view.setCurrentIndex(index)
        self.tile_canvas.update()
        self.tile_canvas.redraw_world()
    
    def selectFistLayerWithTilesetPath(self, path):
        i = dreamscape_config.tileset_layers.indexOfFirstTilesetWithPath(path)
        index = self.model.index(i, 0)
        self.view.setCurrentIndex(index)
        self.tile_canvas.update()
        self.tile_canvas.redraw_world()

    # New method to handle adding a new layer from the context menu
    def add_new_layer(self):
        layer_name, ok = QInputDialog.getText(self, "New Layer", "Enter name for the new layer:")
        # Check if the user clicked OK and provided a name.
        while not layer_name.strip() and ok:
            QMessageBox.warning(self, 'Empty Entry', 'Layer name cannot be empty.')
            layer_name, ok = QInputDialog.getText(self, "New Layer", "Enter name for the new layer:")
            
        if ok and layer_name:
            if dreamscape_config.tileset_layers.layerNameExists(layer_name):
                QMessageBox.warning(self, 'Name Already Exists', f'Layer name "{layer_name}" already exists.')
            else:
                self.addLayer(layer_name, dreamscape_config.tileset_layers.active_layer_path)
    
    # New method to handle removing the selected layer from the context menu
    def remove_selected_layer(self):
        current_index = self.get_selected_layer_index()
        if dreamscape_config.tileset_layers.length() == 1:
            QMessageBox.warning(self, 'Cannot Remove Layer', 'There must be at least one layer in the editor.')
            return
        
        if current_index != -1:  # Ensure a layer is selected
            button = QMessageBox.warning(self, 'Remove Layer', f'Are you sure you want to remove layer "{dreamscape_config.tileset_layers.active_layer_name}"?', QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if button == QMessageBox.StandardButton.Ok:
                if(dreamscape_config.tileset_layers.onlyLayerWithTileset(dreamscape_config.tileset_layers.active_layer_name)):
                    QMessageBox.warning(self, 'Last Tileset Layer', 'This Layer is associated with a tileset, cannont remove.')
                    return
                self.model.beginRemoveRows(QModelIndex(), current_index, current_index)
                del self.model.layers[current_index]
                dreamscape_config.tileset_layers.removeTilesetLayerAtIndex(current_index)
                self.model.endRemoveRows()
                index = self.model.index(0, 0)
                self.view.setCurrentIndex(index)
                self.tile_canvas.update()
                self.tile_canvas.redraw_world()
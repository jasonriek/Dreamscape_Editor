from PySide6.QtCore import (QAbstractListModel, Signal, Qt, QModelIndex, QMimeData, QByteArray, QDataStream, QIODevice)

import ds

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
        visibility = ds.data.layers.layer_visibility[old_layer_index]
        if visibility:
            hidden_label = '' 
        return {'name': f'[Layer {new_layer_index + 1}]   ({layer_name}) {hidden_label}'}

    def swapRows(self, row1, row2):
        if 0 <= row1 < self.rowCount() and 0 <= row2 < self.rowCount():
            layer_1_name = ds.data.layers.getLayerNameByIndex(row2)
            layer_2_name = ds.data.layers.getLayerNameByIndex(row1)
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
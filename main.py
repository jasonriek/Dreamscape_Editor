import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QStyledItemDelegate, QStyleOptionViewItem, QItemDelegate, QPushButton, QScrollArea, QVBoxLayout, QWidget, QDockWidget, QFileDialog,
QListWidget, QListWidgetItem, QCheckBox, QHBoxLayout, QListView, QStyle, QAbstractItemView, QMenu, QInputDialog, QMessageBox)

from PySide6.QtGui import QPixmap, QImage, QPainter, QMouseEvent, QAction, QIcon
from PySide6.QtCore import (Qt, QAbstractListModel, QModelIndex, QMimeData, QByteArray, QDataStream,
                            QIODevice, Signal, QEvent, QRect)

from tileset_data import TilesetLayers

TILE_SIZE = 32
WORLD_WIDTH = 150
WORLD_HEIGHT = 150
DISPLAY_WIDTH = TILE_SIZE * WORLD_WIDTH
DISPLAY_HEIGHT = TILE_SIZE * WORLD_HEIGHT

CHECKER_SIZE = 16
LIGHT_GRAY = Qt.GlobalColor.lightGray
WHITE = Qt.GlobalColor.white

tileset_layers = TilesetLayers()
tileset_layers.appendTilesetLayer('Cyber Punk 1','cyberpunk_1_assets_1.png',32,32)
tileset_layers.appendTilesetLayer('Cyber Punk 2','cyberpunk_1_assets_1.png',32,32)


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

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
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

    def swapRows(self, row1, row2):
        if 0 <= row1 < self.rowCount() and 0 <= row2 < self.rowCount():
            self.layers[row1], self.layers[row2] = self.layers[row2], self.layers[row1]
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
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.view = QListView(self)
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

        # Create sample layers for this example
        for i in range(tileset_layers.length()):
            layer = {'name': f"Layer {i+1} ({tileset_layers.getLayerNameByIndex(i)})", 'visible': True}
            self.model.addLayer(layer)

    def layer_changed(self, current, previous):
        tileset_layers.active_layer_name = tileset_layers.getLayerNameByIndex(current.row())

    def layer_swapped(self, row1, row2):
        self.canvas.swap_layers(row1, row2)

    def get_selected_layer_index(self):
        return self.view.selectionModel().currentIndex().row()
    
    def updateVisibility(self, state):
        tileset_layers.changeVisibility(state)
        self.canvas.update()
        self.canvas.redraw_world()

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
            visible_action.setChecked(tileset_layers.layer_visibilty[index.row()])
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

    # New method to handle adding a new layer from the context menu
    def add_new_layer(self):
        layer_name, ok = QInputDialog.getText(self, "New Layer", "Enter name for the new layer:")
        # Check if the user clicked OK and provided a name.
        while not layer_name.strip() and ok:
            QMessageBox.warning(self, 'Empty Entry', 'Layer name cannot be empty.')
            layer_name, ok = QInputDialog.getText(self, "New Layer", "Enter name for the new layer:")
            
        if ok and layer_name:
            if tileset_layers.layerNameExists(layer_name):
                QMessageBox.warning(self, 'Name Already Exists', f'Layer name "{layer_name}" already exists.')
            else:
                tileset_layers.appendTilesetLayer(layer_name, tileset_layers.active_layer_path, 32, 32)
                tileset_layers.layer_pixmaps.append(QPixmap(DISPLAY_WIDTH, DISPLAY_HEIGHT))
                row = self.model.rowCount()
                new_layer = {'name': f"Layer {row + 1} ({layer_name})", 'visible': True}
                self.model.addLayer(new_layer)
                index = self.model.index(self.model.rowCount() - 1, 0)
                self.view.setCurrentIndex(index)
                self.canvas.update()
                self.canvas.redraw_world()
                
    # New method to handle removing the selected layer from the context menu
    def remove_selected_layer(self):
        current_index = self.get_selected_layer_index()
        if tileset_layers.length() == 1:
            QMessageBox.warning(self, 'Cannot Remove Layer', 'There must be at least one layer in the editor.')
            return
        
        if current_index != -1:  # Ensure a layer is selected
            button = QMessageBox.warning(self, 'Remove Layer', f'Are you sure you want to remove layer "{tileset_layers.active_layer_name}"?', QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if button == QMessageBox.StandardButton.Ok:
                self.model.beginRemoveRows(QModelIndex(), current_index, current_index)
                del self.model.layers[current_index]
                tileset_layers.removeTilesetLayerAtIndex(current_index)
                self.model.endRemoveRows()
                index = self.model.index(0, 0)
                self.view.setCurrentIndex(index)
                self.canvas.update()
                self.canvas.redraw_world()
                
class TileSelector(QWidget):
    def __init__(self):
        super().__init__()
        tileset_layers.active_layer_path = 'cyberpunk_1_assets_1.png'
        tileset_layers.active_layer_name = 'Cyber Punk 1'
        self.tileset = QImage(tileset_layers.active_layer_path)
        self.setFixedSize(self.tileset.width(), self.tileset.height())
        self.selected_tile = None

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw checkered background
        for x in range(0, self.width(), CHECKER_SIZE):
            for y in range(0, self.height(), CHECKER_SIZE):
                if (x // CHECKER_SIZE) % 2 == 0:
                    color = WHITE if (y // CHECKER_SIZE) % 2 == 0 else LIGHT_GRAY
                else:
                    color = LIGHT_GRAY if (y // CHECKER_SIZE) % 2 == 0 else WHITE

                painter.fillRect(x, y, CHECKER_SIZE, CHECKER_SIZE, color)

        painter.drawImage(0, 0, self.tileset)

        if self.selected_tile:
            tile_x, tile_y = self.selected_tile
            painter.setPen(Qt.GlobalColor.red)
            painter.drawRect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def mousePressEvent(self, event: QMouseEvent):
        x = int(event.position().x()) // TILE_SIZE
        y = int(event.position().y()) // TILE_SIZE
        tileset_layers.selected_x = x
        tileset_layers.selected_y = y
        self.selected_tile = (x, y)
        self.update()  # Trigger a repaint

    def get_selected_tile(self):
        return self.selected_tile

class TileCanvas(QWidget):
    def __init__(self, tile_selector):
        super().__init__()
        self.tile_selector = tile_selector
        self.setFixedSize(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        self.show_grid = True
        tileset_layers.layer_pixmaps = [QPixmap(DISPLAY_WIDTH, DISPLAY_HEIGHT) for _ in range(tileset_layers.length())]
        for pixmap in tileset_layers.layer_pixmaps:
            pixmap.fill(Qt.GlobalColor.transparent)

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Paint tiles from all layers based on visibility
        for layer_index in reversed(range(len(tileset_layers.layer_pixmaps))):
            pixmap = tileset_layers.layer_pixmaps[layer_index]
            if tileset_layers.layer_visibilty[layer_index]:  # Check if this layer should be rendered
                painter.drawPixmap(0, 0, pixmap)

        # Draw the grid if the flag is set
        if self.show_grid:
            painter.setPen(Qt.GlobalColor.black)
            for x in range(0, DISPLAY_WIDTH, TILE_SIZE):
                painter.drawLine(x, 0, x, DISPLAY_HEIGHT)
            for y in range(0, DISPLAY_HEIGHT, TILE_SIZE):
                painter.drawLine(0, y, DISPLAY_WIDTH, y)
        painter.end()

    def draw_tile_on_layer(self, tileset_name, tile_index):
        tile_data = tileset_layers.tile(tileset_name, tile_index)
        if tile_data:
            src_x, src_y, x, y, b = tile_data
            tileset_info = tileset_layers.tilesetLayer(tileset_name)
            tileset_img = QImage(tileset_info['tileset'])
            painter = QPainter(tileset_layers.layer_pixmaps[tileset_layers.layerIndex(tileset_name)])  # Assuming you have one QPixmap per tileset layer
            painter.drawImage(x * tileset_info['tile_width'], y * tileset_info['tile_height'],
                      tileset_img,
                      src_x * tileset_info['tile_width'], src_y * tileset_info['tile_height'],
                      tileset_info['tile_width'], tileset_info['tile_height'])
            painter.end()  # End painting

    def redraw_world(self):
        for tileset_name in tileset_layers.order:
            self.redraw_layer(tileset_name)

    def redraw_layer(self, tileset_name):
        tileset_info = tileset_layers.tilesetLayer(tileset_name)
        tileset_img = QImage(tileset_info['tileset'])
        
        pixmap = QPixmap(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        
        for i, tile_data in enumerate(tileset_info['tiles']):
            src_x, src_y, x, y, b = tile_data
            painter.drawImage(x * TILE_SIZE, y * TILE_SIZE,
                            tileset_img,
                            src_x * tileset_info['tile_width'], src_y * tileset_info['tile_height'],
                            tileset_info['tile_width'], tileset_info['tile_height'])
        tileset_layers.layer_pixmaps[tileset_layers.layerIndex(tileset_name)] = pixmap
        painter.end()  # End painting

    def swap_layers(self, layer1_index, layer2_index):
        # Swap the tilesets in TilesetLayers
        success = tileset_layers.swapLayerOrder(layer1_index, layer2_index)
        if not success:
            print(f"Failed to swap layers: {layer1_index} and {layer2_index}")
            return

        # Redraw every layer to ensure correct stacking order
        for tileset_name in tileset_layers.order:
            self.redraw_layer(tileset_name)
        self.update()  # Trigger a repaint

    def mousePressEvent(self, event: QMouseEvent):
        if not self.tile_selector.get_selected_tile():
            return

        x = int(event.position().x()) // TILE_SIZE
        y = int(event.position().y()) // TILE_SIZE

        # Check if tile already exists here at this layer, if so, replace it.
        current_layer_index = tileset_layers.layerIndex(tileset_layers.active_layer_name)
        tile_index = tileset_layers.getTileIndexFromXY(x, y)
        if tile_index is not None and tile_index >= 0: # update the current tile
            tileset_layers.updateTile(tileset_layers.active_layer_name, tile_index,
                [tileset_layers.selected_x,
                tileset_layers.selected_y,
                x,
                y,
                0]
            )
            # Redraw every layer to ensure correct stacking order
            for tileset_name in tileset_layers.order:
                self.redraw_layer(tileset_name)
        else: # make a new tile
            tile_index = tileset_layers.appendTile(
                tileset_layers.active_layer_name, 
                tileset_layers.selected_x, 
                tileset_layers.selected_y,
                x,
                y,
                0)
        if current_layer_index is not None:
            # Register the tile drawing as an operation for the selected layer
            self.draw_tile_on_layer(tileset_layers.active_layer_name, tile_index)
            self.update()  # Trigger a repaint

    def update_layer_visibility(self):
        self.update()  # Trigger repaint

class ToolDock(QWidget):
    def __init__(self, tile_selector):
        super().__init__()

        self.tile_selector = tile_selector
        layout = QVBoxLayout(self)

        self.load_tileset_btn = QPushButton("Load Tileset")
        self.load_tileset_btn.clicked.connect(self.load_tileset)
        layout.addWidget(self.load_tileset_btn)

        # Additional tools can be added here

    def load_tileset(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Tileset", "", "Images (*.png *.jpg *.bmp)")
        if filepath:
            self.tile_selector.set_tileset(filepath)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        tile_selector = TileSelector()

        # Create and set up the TileSelector dock
        selector_dock = QDockWidget("Tile Selector", self)
        selector_dock.setWidget(tile_selector)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, selector_dock)

        # Create and set up the TileCanvas dock
        canvas_dock = QDockWidget("Tile Canvas", self)
        canvas = TileCanvas(tile_selector)
        layers_widget = Layers(canvas)
        canvas.layers_widget = layers_widget
        scroll_area = QScrollArea()
        scroll_area.setWidget(canvas)
        canvas_dock.setWidget(scroll_area)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, canvas_dock)  # Note: Qt doesn't directly support a "CenterDockWidgetArea". This might place the dock in the default position.

        # Create and set up the ToolDock
        tool_dock = QDockWidget("Tools", self)
        tools = ToolDock(tile_selector)
        tool_dock.setWidget(tools)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, tool_dock)
        layers_dock = QDockWidget('Layers', self)
        layers_dock.setWidget(layers_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, layers_dock)

        self.setWindowTitle("Tilemap Painter with PySide6")
        self.showMaximized()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon_maybe_BIG.ico'))
    app.setStyle('fusion')
    window = MainWindow()
    with open('ds.qss', 'r') as qss:
        window.setStyleSheet(qss.read())
    sys.exit(app.exec())

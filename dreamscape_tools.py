from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog,
    QHBoxLayout, QHeaderView, QLabel, QSizePolicy, QGroupBox, QCheckBox, QLineEdit, QInputDialog, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Signal
import dreamscape_config


class LoadTilesetWidget(QWidget):
    def __init__(self, tileset_bar, tile_canvas, layers_widget):
        super().__init__()
        self.tileset_bar = tileset_bar
        self.tile_canvas = tile_canvas
        self.layers_widget = layers_widget

        self.layers_widget.layerClicked.connect(self.updateByTilesetPath(self.tileset_bar.changeIndexByTilesetPath))
        self.tileset_bar.tilesetChanged.connect(self.updateByTilesetPath(self.layers_widget.selectFistLayerWithTilesetPath))

        self.init_ui()

    def updateByTilesetPath(self, callback):
        def _updateByTilesetPath(tileset_path):
            self.layers_widget.blockSignals(True)
            callback(tileset_path)
            self.layers_widget.blockSignals(False)
            self.tileset_src_entry.setText(tileset_path)
        return _updateByTilesetPath

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.tileset_src_entry = QLineEdit('cyberpunk_1_assets_1.png', readOnly=True)
        self.load_tileset_btn = QPushButton("Browse", clicked=self.load_tileset)

        layout.addWidget(QLabel('Tileset Path:'))
        layout.addWidget(self.tileset_src_entry)
        layout.addWidget(self.load_tileset_btn)

        self.setLayout(layout)
    
    def tilesetPath(self):
        return self.tileset_src_entry.text()

    def load_tileset(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Tileset", "", "Images (*.png *.jpg *.bmp)")
        if path:

            tileset_name, ok = QInputDialog.getText(self, "New Tileset", "Enter name for the new tileset:")
            # Check if the user clicked OK and provided a name.
            while not tileset_name.strip() and ok:
                QMessageBox.warning(self, 'Empty Entry', 'Layer name cannot be empty.')
                tileset_name, ok = QInputDialog.getText(self, "New Tileset", "Enter name for the new tileset:")
            
            while dreamscape_config.tileset_layers.layerNameExists(tileset_name) and ok:
                QMessageBox.warning(self, 'Name Already Exists', f'Layer name "{tileset_name}" already exists.')
                tileset_name, ok = QInputDialog.getText(self, "New Tileset", "Enter name for the new tileset:")

            if ok and tileset_name:
                self.tileset_src_entry.setText(path)
                self.tileset_bar.addTileset(tileset_name, path)
                self.layers_widget.addLayer(tileset_name, path)
            
class ActiveTileWidget(QWidget):
    worldTileClicked = Signal(int, int)
    def __init__(self, tile_canvas):
        super().__init__()
        self.tile_canvas = tile_canvas
        # Initialize the active tile display and checkbox
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # Create the layout
        self.gbox1 = QGroupBox(self, 'Selected Tile')
        self.gbox1_layout = QHBoxLayout(self.gbox1)
        self.gbox2 = QGroupBox(self, 'Base Tile')
        self.gbox2_layout = QHBoxLayout(self.gbox2)
        filler_1 = QWidget(self)
        filler_1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        filler_2 = QWidget(self)
        filler_2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Create the QLabel for displaying the active tile
        label1 = QLabel('Selected Tile: ')
        self.active_tile_label = QLabel(self)
        self.active_tile_label.setFixedSize(32, 32)  # Set size to 32x32
        self.gbox1_layout.addWidget(label1)
        self.gbox1_layout.addWidget(self.active_tile_label)
        # Create the QCheckBox for setting the tile as base
        self.base_tile_button = QPushButton("Set as base tile", self)
        self.base_tile_button.clicked.connect(self.setBaseTile)
        self.hide_base_tile_checkbox = QCheckBox('Hide', self)
        self.hide_base_tile_checkbox.stateChanged.connect(self.hideBaseTiles)
        self.gbox1_layout.addWidget(self.base_tile_button)
        self.gbox1_layout.addWidget(filler_1)
        self.collision_checkbox = QCheckBox('Has Collision', self)
        self.overlay_checkbox = QCheckBox('Overylay', self)
        self.gbox1_layout.addWidget(self.collision_checkbox)
        self.gbox1_layout.addWidget(self.overlay_checkbox)

        label2 = QLabel('Base Tile:    ')
        self.base_tile_label = QLabel(self)
        self.base_tile_label.setFixedSize(32, 32)
        self.gbox2_layout.addWidget(label2)
        self.gbox2_layout.addWidget(self.base_tile_label)
        self.gbox2_layout.addWidget(self.hide_base_tile_checkbox)
        self.gbox2_layout.addWidget(filler_2)

        # Set the layout to the ActiveTileWidget
        layout.addWidget(self.gbox1)
        layout.addWidget(self.gbox2)
        self.setLayout(layout)

    # This function can be called when the selected tile changes
    def update_active_tile_display(self, image):
        pixmap = QPixmap.fromImage(image)
        self.active_tile_label.setPixmap(pixmap)
    
    def setBaseTile(self):
        self.base_tile_label.setPixmap(self.active_tile_label.pixmap().copy())
        dreamscape_config.tileset_layers.base_tile_src = dreamscape_config.tileset_layers.active_layer_path
        dreamscape_config.tileset_layers.base_tile_src_x = dreamscape_config.tileset_layers.selected_x
        dreamscape_config.tileset_layers.base_tile_src_y = dreamscape_config.tileset_layers.selected_y
        dreamscape_config.tileset_layers.base_tile_src_w = 32
        dreamscape_config.tileset_layers.base_tile_src_h = 32
        self.tile_canvas.drawBaseTiles()
        self.tile_canvas.redraw_world()
        self.tile_canvas.update()
    
    def hideBaseTiles(self, hide):
        dreamscape_config.tileset_layers.base_tiles_visible = not bool(hide)
        if dreamscape_config.tileset_layers.base_pixmap:
            self.tile_canvas.redraw_world()
            self.tile_canvas.update()

    def updateTileProperties(self, tile):
        self.worldTileClicked.emit(tile[0], tile[1])
        self.collision_checkbox.setChecked(bool(tile[4]))
        self.overlay_checkbox.setChecked(bool(tile[5]))  

class Tools(QWidget):
    def __init__(self, tileset_bar, tile_canvas, layers_widget):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self.tile_setloader = LoadTilesetWidget(tileset_bar, tile_canvas, layers_widget)
        self.tile_canvas = tile_canvas
        self._layout.addWidget(self.tile_setloader)
        self.export_json_button = QPushButton('Export JSON')
        self.export_json_button.clicked.connect(self.exportJson)

        self.tile_selector = tileset_bar.tile_selector
        # Additional tools can be added here
        self.tile_table = QTableWidget(2, 1)  # 1 row, 4 columns
        self.tile_table.setHorizontalHeaderLabels(["Tile Information"])
        self.tile_table.setVerticalHeaderLabels(["World Coord.", "Tile Selection"])
        self.tile_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tile_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tile_selector.tileSelected.connect(self.setTileXYInTileTable)
        self.tile_canvas.mouseMoved.connect(self.setWorldXYInTileTable)

        self._layout.addWidget(self.tile_table)
    
    def setTileXYInTileTable(self, x, y):
        self.tile_table.setItem(0, 1, QTableWidgetItem(f"({str(x)}, {str(y)})"))

    def setWorldXYInTileTable(self, x, y):
        self.tile_table.setItem(0, 0, QTableWidgetItem(f"({str(x)}, {str(y)})"))
    
    def exportJson(self):
        with open('test.json', 'w') as f, open('test_overlay.json', 'w') as fo:
            game, game_overlay = dreamscape_config.tileset_layers.getJson()
            f.write(game)
            fo.write(game_overlay)

    
    def setInternalWidgets(self):
        self._layout.addWidget(self.export_json_button)
        #self._layout.addWidget(self.tile_setloader)

    def addToLayout(self, widget):
        self._layout.addWidget(widget)
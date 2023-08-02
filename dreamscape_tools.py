from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout, QLabel, QSizePolicy, QGroupBox, QCheckBox, QLineEdit, QInputDialog, QMessageBox)
from PySide6.QtGui import (QPixmap, QImage)
import dreamscape_config

class LoadTilesetWidget(QWidget):
    def __init__(self, tile_selector, tile_canvas, layers_widget):
        super().__init__()
        self.tile_selector = tile_selector
        self.tile_canvas = tile_canvas
        self.layers_widget = layers_widget

        # Initialize the active tile display and checkbox
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        # Create the layout

        # Set the layout to the ActiveTileWidget
        label = QLabel('Tileset:')
        self.tileset_src_entry = QLineEdit(self)
        self.tileset_src_entry.setText('cyberpunk_1_assets_1.png')
        self.tileset_src_entry.setReadOnly(True)
        self.load_tileset_btn = QPushButton("Browse")
        self.load_tileset_btn.clicked.connect(self.load_tileset)
        layout.addWidget(label)
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
                self.tile_selector.setTileset(tileset_name, path)
                self.layers_widget.addLayer(tileset_name, path)
            


class ActiveTileWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the active tile display and checkbox
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # Create the layout
        self.gbox1 = QGroupBox(self, 'Active Tile')
        self.gbox1_layout = QHBoxLayout(self.gbox1)
        self.gbox2 = QGroupBox(self, 'Base Tile')
        self.gbox2_layout = QHBoxLayout(self.gbox2)
        filler_1 = QWidget(self)
        filler_1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        filler_2 = QWidget(self)
        filler_2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Create the QLabel for displaying the active tile
        label1 = QLabel('Active Tile: ')
        self.active_tile_label = QLabel(self)
        self.active_tile_label.setFixedSize(32, 32)  # Set size to 32x32
        self.gbox1_layout.addWidget(label1)
        self.gbox1_layout.addWidget(self.active_tile_label)
        # Create the QCheckBox for setting the tile as base
        self.base_tile_checkbox = QCheckBox("Set as base tile", self)
        self.gbox1_layout.addWidget(self.base_tile_checkbox)
        self.gbox1_layout.addWidget(filler_1)
        # Create the QCheckBox for setting the tile as base
        label2 = QLabel('Base Tile: ')
        self.base_tile_label = QLabel(self)
        self.base_tile_label.setFixedSize(32, 32)
        self.gbox2_layout.addWidget(label2)
        self.gbox2_layout.addWidget(self.base_tile_label)
        self.gbox2_layout.addWidget(filler_2)

        # Set the layout to the ActiveTileWidget
        layout.addWidget(self.gbox1)
        layout.addWidget(self.gbox2)
        self.setLayout(layout)


    # This function can be called when the selected tile changes
    def update_active_tile_display(self, image):
        pixmap = QPixmap.fromImage(image)
        self.active_tile_label.setPixmap(pixmap)


class Tools(QWidget):
    def __init__(self, tile_selector, tile_canvas, layers_widget):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self.tile_setloader = LoadTilesetWidget(tile_selector, tile_canvas, layers_widget)
        self._layout.addWidget(self.tile_setloader)

        # Additional tools can be added here
    
    def setInternalWidgets(self):
        pass
        #self._layout.addWidget(self.tile_setloader)

    def addToLayout(self, widget):
        self._layout.addWidget(widget)
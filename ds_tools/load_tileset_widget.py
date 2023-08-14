from PySide6.QtWidgets import (QWidget, QPushButton, QFileDialog, QHBoxLayout,  QLabel, QLineEdit, QInputDialog, QMessageBox)

import ds


class LoadTilesetWidget(QWidget):
    def __init__(self, tileset_bar, tile_canvas, layers):
        super().__init__()
        self.tileset_bar = tileset_bar
        self.tile_canvas = tile_canvas
        self.layers = layers

        self.layers.layerClicked.connect(self.updateByTilesetPath(self.tileset_bar.changeIndexByTilesetPath))
        self.tileset_bar.tilesetChanged.connect(self.updateByTilesetPath(self.layers.selectFistLayerWithTilesetPath))

        self.init_ui()

    def updateByTilesetPath(self, callback):
        def _updateByTilesetPath(tileset_path):
            self.layers.blockSignals(True)
            callback(tileset_path)
            self.layers.blockSignals(False)
            self.tileset_src_entry.setText(tileset_path)
        return _updateByTilesetPath

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.tileset_src_entry = QLineEdit(readOnly=True)
        self.load_tileset_btn = QPushButton("Browse", clicked=self.loadTileset)

        layout.addWidget(QLabel('Tileset Path:'))
        layout.addWidget(self.tileset_src_entry)
        layout.addWidget(self.load_tileset_btn)

        self.setLayout(layout)
    
    def tilesetPath(self):
        return self.tileset_src_entry.text()

    def loadTileset(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Tileset", "", "Images (*.png *.jpg *.bmp)")
        if path:

            tileset_name, ok = QInputDialog.getText(self, "New Tileset", "Enter name for the new tileset:")
            # Check if the user clicked OK and provided a name.
            while not tileset_name.strip() and ok:
                QMessageBox.warning(self, 'Empty Entry', 'Layer name cannot be empty.')
                tileset_name, ok = QInputDialog.getText(self, "New Tileset", "Enter name for the new tileset:")
            
            while ds.data.layers.layerNameExists(tileset_name) and ok:
                QMessageBox.warning(self, 'Name Already Exists', f'Layer name "{tileset_name}" already exists.')
                tileset_name, ok = QInputDialog.getText(self, "New Tileset", "Enter name for the new tileset:")

            if ok and tileset_name:
                self.tileset_src_entry.setText(path)
                self.tileset_bar.addTileset(tileset_name, path)
                self.layers.addLayer(tileset_name, path)
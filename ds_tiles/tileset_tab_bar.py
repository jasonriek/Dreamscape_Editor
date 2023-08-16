from PySide6.QtWidgets import (QWidget, QTabBar, QVBoxLayout)
from PySide6.QtCore import (Signal)

from .tileset_scroll_area import TilesetScrollArea

import ds


class TilesetTabBar(QWidget):
    tilesetChanged = Signal(str)
    def __init__(self):
        super().__init__()

        # Create the TileSelector and QTabBar
        self.tileset_scroll_area = TilesetScrollArea()
        self.tile_selector = self.tileset_scroll_area.tile_selector
        self.removing_tab = False
        self.tab_bar = QTabBar()
        self.tab_bar.setExpanding(False)
        self.tab_bar.setStyleSheet("""
            QTabBar::tab {
                min-width: 100px;
            }
        """)
        # Connect tab change to update function
        self.tab_bar.currentChanged.connect(self.changeTileset)

        # Layout
        self._layout = QVBoxLayout()
        self._layout.addWidget(self.tab_bar)
        self._layout.addWidget(self.tileset_scroll_area)
        self.setLayout(self._layout)

        # Dictionary to store tilesets paths associated with tab indexes
        self.tilesets = {}

        #self.addTileset('Cyber Punk 1', 'cyberpunk_1_assets_1.png')
    
    def changeIndexByTilesetPath(self, tileset_path):
        for i in range(self.tab_bar.count()):
            if self.tilesets[i][1] == tileset_path:
                self.tab_bar.setCurrentIndex(i)
                break
    
    def reIndexTabs(self):
        _tilesets = {}
        for i, _i in enumerate(self.tilesets.keys()):
            _tilesets[i] = self.tilesets[_i]
        self.tilesets = _tilesets

    def removeTabByTilesetPath(self, tileset_path:str):
        self.removing_tab = True
        print(f"Received signal to remove tileset: {tileset_path}")
        for i in range(self.tab_bar.count()):
            if self.tilesets[i][1] == tileset_path:
                self.tab_bar.removeTab(i)
                last_tab_index = self.tab_bar.count() - 1
                del self.tilesets[i]
                self.reIndexTabs()
                if last_tab_index >= 0:
                    self.tab_bar.setCurrentIndex(last_tab_index)
                    ds.data.layers.active_layer_name = self.tilesets[last_tab_index][0]
                    ds.data.layers.active_layer_src = self.tilesets[last_tab_index][1]
                    if last_tab_index == 0:
                        self.changeTileset(0)
                break

    def addTileset(self, tileset_name:str, tileset_path:str):
        self.tile_selector.setTileset(tileset_name, tileset_path)
        index = self.tab_bar.addTab(tileset_name)
        self.tilesets[index] = (tileset_name, tileset_path)
        # If it's the first tileset, set it immediately
        if self.tab_bar.count() == 1:
            self.changeTileset(0)

    def changeTileset(self, index):
        if not self.removing_tab:
            tileset_data = self.tilesets.get(index)
            if tileset_data:
                self.tile_selector.changeTileset(tileset_data[0], tileset_data[1])
                self.tilesetChanged.emit(tileset_data[1])
        else:
            self.removing_tab = False
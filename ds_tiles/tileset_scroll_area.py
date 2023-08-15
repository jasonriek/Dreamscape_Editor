from PySide6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea)

from .tile_selector import TileSelector

class TilesetScrollArea(QWidget):
    def __init__(self):
        super().__init__()

        # Create an instance of the TileSelector
        self.tile_selector = TileSelector()

        # Create a QScrollArea and set its properties
        self.scroll_area = QScrollArea(self)
        #self.setFixedSize(320, 320)
        self.setMinimumWidth(288)
        self.setMinimumHeight(256)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setWidget(self.tile_selector)

        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
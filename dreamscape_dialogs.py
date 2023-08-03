from PySide6.QtWidgets import (QDialog, QSpinBox, QPushButton, QGridLayout, QLabel)

class WorldSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set World Size")

        # Create SpinBoxes for width and height
        self.width_spinbox = QSpinBox(self)
        self.height_spinbox = QSpinBox(self)

        # Set properties for the SpinBoxes
        self.width_spinbox.setMinimum(1)
        self.height_spinbox.setMinimum(1)

        # Create OK and Cancel buttons
        self.button_ok = QPushButton("OK", self)
        self.button_ok.clicked.connect(self.accept)
        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.reject)

        # Layout for the dialog
        layout = QGridLayout(self)
        layout.addWidget(QLabel("Width:"), 0, 0)
        layout.addWidget(self.width_spinbox, 0, 1)
        layout.addWidget(QLabel("Height:"), 1, 0)
        layout.addWidget(self.height_spinbox, 1, 1)
        layout.addWidget(self.button_ok, 2, 0)
        layout.addWidget(self.button_cancel, 2, 1)

        self.setLayout(layout)

    def get_values(self):
        return (self.width_spinbox.value(), self.height_spinbox.value())

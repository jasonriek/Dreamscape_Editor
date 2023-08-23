from PySide6.QtWidgets import QDialog, QWidget, QTabWidget, QHBoxLayout, QSizePolicy, QMessageBox, QVBoxLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QApplication

import ds


class DoorDialog(QDialog):
    def __init__(self):
        super(DoorDialog, self).__init__()
        self.setWindowTitle('Door')
        self.setLayout(QVBoxLayout())
        self.setMinimumWidth(400)

        # Name
        self.name_label = QLabel("Name:")
        self.name_edit = QLineEdit()

        self.tabs = QTabWidget(self)
        self.main_widght = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widght)

        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(self.name_edit)

        self.bottom_buttons_area = QWidget(self)
        self.bottom_buttons_layout = QHBoxLayout(self.bottom_buttons_area)
        self.button_filler = QWidget(self)
        self.button_filler.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Destination
        self.destination_label = QLabel('Destination:')
        self.destination_edit = QLineEdit()
        self.main_layout.addWidget(self.destination_label)
        self.main_layout.addWidget(self.destination_edit)

        # Entrance Direction
        self.entrance_direction_label = QLabel("Entrance Direction:")
        self.entrance_direction_combo = QComboBox()
        self.entrance_direction_combo.addItems(['North', 'South', 'East', 'West'])
        self.main_layout.addWidget(self.entrance_direction_label)
        self.main_layout.addWidget(self.entrance_direction_combo)

        # Entrance X and Y
        self.entrance_x_label = QLabel("Entrance X:")
        self.entrance_x_spin = QSpinBox()
        self.entrance_x_spin.setMaximum(999999)
        self.main_layout.addWidget(self.entrance_x_label)
        self.main_layout.addWidget(self.entrance_x_spin)

        self.entrance_y_label = QLabel("Entrance Y:")
        self.entrance_y_spin = QSpinBox()
        self.entrance_y_spin.setMaximum(999999)
        self.main_layout.addWidget(self.entrance_y_label)
        self.main_layout.addWidget(self.entrance_y_spin)

        # Exit X and Y
        self.exit_x_label = QLabel("Exit X:")
        self.exit_x_spin = QSpinBox()
        self.exit_x_spin.setMaximum(999999)
        self.main_layout.addWidget(self.exit_x_label)
        self.main_layout.addWidget(self.exit_x_spin)

        self.exit_y_label = QLabel("Exit Y:")
        self.exit_y_spin = QSpinBox()
        self.exit_y_spin.setMaximum(999999)
        self.main_layout.addWidget(self.exit_y_label)
        self.main_layout.addWidget(self.exit_y_spin)

        # Exit Direction
        self.exit_direction_label = QLabel("Exit Direction:")
        self.exit_direction_combo = QComboBox()
        self.exit_direction_combo.addItems(['North', 'South', 'East', 'West'])
        self.main_layout.addWidget(self.exit_direction_label)
        self.main_layout.addWidget(self.exit_direction_combo)

        # OK and Cancel buttons
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.onAccept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.tabs.addTab(self.main_widght, 'Settings')
        self.layout().addWidget(self.tabs)
        self.bottom_buttons_layout.addWidget(self.button_filler)
        self.bottom_buttons_layout.addWidget(self.ok_button)
        self.bottom_buttons_layout.addWidget(self.cancel_button)
        self.layout().addWidget(self.bottom_buttons_area)

        self.door = None
        self.tile_width = ds.data.world.tile_width
        self.tile_height = ds.data.world.tile_height
        self.old_name = ''
    
    def setValues(self, x:int, y:int):
        self.door = ds.data.world.doorFromXY(x, y)
        if self.door is not None:
            self.old_name = self.door['name']
            self.name_edit.setText(self.door['name'])
            self.destination_edit.setText(self.door['destination'])
            self.exit_direction_combo.setCurrentText(self.door['direction'])
            self.entrance_x_spin.setValue(self.door['x'])
            self.entrance_y_spin.setValue(self.door['y'])
            self.exit_x_spin.setValue(self.door['exit_position']['x'])
            self.exit_y_spin.setValue(self.door['exit_position']['y'])

    def getValues(self):
        if self.door:
            self.tile_width = self.door['tile_width']
            self.tile_height = self.door['tile_height']
        return {
            'name': self.name_edit.text(),
            'destination': self.destination_edit.text(),
            'direction': self.entrance_direction_combo.currentText(),
            'x': self.entrance_x_spin.value(),
            'y': self.entrance_y_spin.value(),
            'tile_width': self.tile_width,
            'tile_height': self.tile_height,
            'exit_position': {
                'x': self.exit_x_spin.value(),
                'y': self.exit_y_spin.value(),
                'direction': self.exit_direction_combo.currentText()
            }
        }
    
    def onAccept(self):
        # Validation
        if not self.name_edit.text().strip() or not self.destination_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please ensure all fields are filled out!")
            return

        # If validation passed
        self.accept()
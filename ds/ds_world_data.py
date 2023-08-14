

class Weather:
    NO_WEATHER = 0
    RAIN = 1
    SNOW = 2
    FOG = 3

class WorldData:
    def __init__(self, parent=None):
        self.parent = parent
        self.name = 'World'
        self.width = 40
        self.height = 40
        self.weather = Weather.RAIN
        self.tile_width = 32
        self.tile_height = 32
        self.barrier = 0
        self.overylay = 0
        self.selected_tile_x = 0
        self.selected_tile_y = 0
        self.player_start_position_x = 0
        self.player_start_position_y = 0
        self.doors = []

    def displayWidth(self):
        """Retrieve the display width."""
        return self.width * self.parent.TILE_SIZE

    def displayHeight(self):
        """Retrieve the display height."""
        return self.height * self.parent.TILE_SIZE
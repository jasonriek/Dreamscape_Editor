

class Weather:
    NO_WEATHER = 0
    RAIN = 1
    SNOW = 2
    FOG = 3

class WorldData:
    def __init__(self, parent=None):
        self.parent = parent
        self.name = 'World'
        self._base_width = 40  # base dimensions
        self._base_height = 40
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
    
    def width(self):
        # Calculating width based on the reference tile size
        scale_factor = 32 / self.tile_width
        return int(self._base_width * scale_factor)
    
    def height(self):
        # Calculating height based on the reference tile size
        scale_factor = 32 / self.tile_height
        return int(self._base_height * scale_factor)

    def setWidth(self, width:int):
        """Set the base width (in units of 32 px tiles)."""
        self._base_width = width
    
    def setHeight(self, height:int):
        """Set the base height (in units of 32 px tiles)."""
        self._base_height = height

    def displayWidth(self):
        """Retrieve the display width."""
        return self.width() * self.tile_width

    def displayHeight(self):
        """Retrieve the display height."""
        return self.height() * self.tile_height
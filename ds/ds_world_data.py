

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
        self.doors = {}
        self.doors_xy = {}

    def doorExists(self, name:str):
        return self.doors.get(name) is not None

    def doorNames(self):
        return list(self.doors.keys())

    def createDoor(self, name:str, destination:str, entrance_x:int, entrance_y:int, tile_width:int, tile_height:int, entrance_direction:str, exit_x:int, exit_y:int, exit_direction:str):
        if self.doorExists(name):
            return
        
        door = {
            'name': name,
            'destination': destination,
            'x': entrance_x,
            'y': entrance_y,
            'tile_width': tile_width,
            'tile_height': tile_height,
            'direction': entrance_direction,
            'exit_position': {
                'x': exit_x,
                'y': exit_y,
                'direction': exit_direction
            }
        }
        self.doors_xy[(entrance_x, entrance_y)] = name
        self.doors[name] = door

    def door(self, name:str):
        return self.doors.get(name)
    
    def doorNameFromXY(self, x:int, y:int):
        return self.doors_xy.get((x,y))

    def doorFromXY(self, x:int, y:int):
        name = self.doorNameFromXY(x, y)
        if name is not None:
            return self.doors.get(name)
        return None

    def updateDoor(self, name:str, door):
        if self.doorExists(name):
            old_x = self.doors[name]['x']
            old_y = self.doors[name]['y']
            new_name = door['name']
            new_x = door['x']
            new_y = door['y']
            del self.doors_xy[(old_x,old_y)]
            self.doors_xy[(new_x,new_y)] = new_name
            self.doors[new_name] = door
            if new_name != name:
                del self.doors[name]

    def removeDoor(self, name:str):
        if self.doorExists(name):
            door = self.door(name)
            x = door['x']
            y = door['y']
            del self.doors_xy[(x,y)]
            del self.doors[name]
    
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
import json
import copy
from PySide6.QtGui import (QPainter, QPixmap)

class TilesetLayers:
    def __init__(self):
        # Base attributes
        self.name = 'World'
        self.weather = True
        self.base_tiles_visible = True
        self.tile_w = 32
        self.tile_h = 32
        self.barrier = 0
        self.overylay = 0
        self.selected_x = 0
        self.selected_y = 0
        self.world_size_width = 150
        self.world_size_height = 150
        self.start_position_x = 0
        self.start_position_y = 0
        self.base_tile_src = ''
        self.base_tile_src_x = 0
        self.base_tile_src_y = 0
        self.base_tile_src_w = 32
        self.base_tile_src_h = 32
        self.doors = []

        # Layer attributes
        self.active_layer_path = ''
        self.active_layer_name = ''
        self.layers = {}
        self.order = []
        self.layer_visibility = []
        self.layer_pixmaps = []
        self.base_pixmap = None
        self.position_to_index_map = {}

        # Initialize position index map
        self.buildPositionIndexMap()

    def __deepcopy__(self, memo):
        new_obj = TilesetLayers()
            
        # Manually deep copy simple attributes
        for attr, value in self.__dict__.items():
            if attr not in ['layer_pixmaps', 'base_pixmap']:
                setattr(new_obj, attr, copy.deepcopy(value, memo))

        # Clone the pixmaps in layer_pixmaps
        new_obj.layer_pixmaps = [self._clone_pixmap(pixmap) for pixmap in self.layer_pixmaps]
            
        # Clone the base_pixmap
        new_obj.base_pixmap = self._clone_pixmap(self.base_pixmap)

        return new_obj

    def _clone_pixmap(self, pixmap):
        if pixmap is None:
            return None
            
        new_pixmap = QPixmap(pixmap.size())
        painter = QPainter(new_pixmap)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return new_pixmap

    def buildPositionIndexMap(self):
        """Builds the position to index map for each layer."""
        for layer_name, layer_data in self.layers.items():
            pos_map = {}
            for i, tile in enumerate(layer_data['tiles']):
                x, y = tile[2], tile[3]
                pos_map[(x, y)] = i
            self.position_to_index_map[layer_name] = pos_map

    def getTileIndexFromXY(self, x, y):
        """Retrieve tile index from x,y coordinates."""
        return self.position_to_index_map.get(self.active_layer_name, {}).get((x, y))

    def displayWidth(self):
        """Retrieve the display width."""
        return self.world_size_width * self.tile_w

    def displayHeight(self):
        """Retrieve the display height."""
        return self.world_size_height * self.tile_h
    
    def getActiveLayerIndex(self):
        if self.active_layer_name in self.order:
            return self.order.index(self.active_layer_name)
        return None

    def getPathByLayerName(self, layer_name:str):
        for layer in self.layers.values():
            if layer['name'] == layer_name:
                return layer['tileset']
        return None

    def changeVisibility(self, state:bool):
        index = self.layerIndex(self.active_layer_name)
        self.layer_visibility[index] = state

    def getLayerNameByIndex(self, index:str):
        """Retrieve the layer name by its index."""
        if index >= 0 and index < len(self.order):
            return self.order[index]
        return None
    
    def tilesetNameExists(self, name: str):
        """Check if a tileset name exists."""
        return name in self.order
    
    def tileExists(self, tileset_name:str, index:int):
        """Check if a tile exists in a given tileset."""
        if index is not None and self.tilesetNameExists(tileset_name):
            return index >= 0 and index < len(self.layers[tileset_name]['tiles'])
        return False
    
    def layerNameExists(self, layer_name: str):
        """Check if a layer name exists."""
        return layer_name.lower() in (name.lower() for name in self.order)
            
    def appendTilesetLayer(self, tileset_name: str, src: str, tile_w: int, tile_h: int, tiles=None, z=0):
        """Append a new tileset layer."""
        if tiles is None:
            tiles = []

        if tileset_name not in self.order:
            self.order.append(tileset_name)
            self.layer_visibility.append(True)
            self.layers[tileset_name] = {
                'name': tileset_name,
                'tileset': src,
                'tile_width': tile_w,
                'tile_height': tile_h,
                'z': z,
                'tiles': tiles   
            }
            self.buildPositionIndexMap()
        else:
            print(f'Tileset name "{tileset_name} already exists')

    def tilesetLayer(self, tileset_name: str):
        return self.layers.get(tileset_name)
    
    def layerIndex(self, tileset_name: str):
        if tileset_name in self.order:
            return self.order.index(tileset_name)
        return None

    def updateTilesetLayer(self, tileset_name: str, src: str, tile_w: int, tile_h: int, tiles: list, z=0):
        if tileset_name in self.order:
            self.layers[tileset_name]['name'] = tileset_name
            self.layers[tileset_name]['tileset'] = src
            self.layers[tileset_name]['tile_width'] = tile_w
            self.layers[tileset_name]['tile_height'] = tile_h
            self.layers[tileset_name]['tiles'] = tiles
            self.layers[tileset_name]['z'] = z

    def swapLayerOrder(self, layer_1_index, layer_2_index):
        if (layer_1_index >= 0 and layer_1_index < len(self.order) and (layer_2_index >= 0 and layer_2_index < len(self.order))):
            layer_1_tileset_name = self.order[layer_1_index]
            layer_2_tileset_name = self.order[layer_2_index]
            self.order[layer_1_index] = layer_2_tileset_name
            self.order[layer_2_index] = layer_1_tileset_name
            return True
        return False
    
    def lastTileset(self, tileset_path:str):
        count = 0
        for layer in self.layers.values():
            if layer['tileset'] == tileset_path:
                count += 1
        return count == 1

    def onlyLayerWithTileset(self, layer_name):
        count = 0
        tileset = self.layers[layer_name]['tileset']
        for layer in self.layers.values():
            if layer['tileset'] == tileset:
                count += 1
        return count == 1
    
    def indexOfFirstTilesetWithPath(self, tileset_path):
        for i, layer in enumerate(self.order):
            if self.layers[layer]['tileset'] == tileset_path:
                return i
        return None

    def removeTilesetLayerAtIndex(self, index:int):
        if index >= 0 and index < len(self.order):
            tileset_name = self.order.pop(index)
            visible = self.layer_visibility.pop(index)
            pixmap = self.layer_pixmaps.pop(index)
            layer = self.layers.pop(tileset_name)
            self.buildPositionIndexMap()
            return layer
        return None
    
    def appendTile(self, tileset_name: str, src_x: int, src_y: int, x: int, y: int, b=0, overlay=0):
        if self.layers.get(tileset_name):
            self.layers[tileset_name]['tiles'].append([
                src_x,
                src_y,
                x,
                y,
                b,
                overlay
            ])
            self.buildPositionIndexMap()
            return len(self.layers[tileset_name]['tiles']) - 1
        return None
    
    def tile(self, tileset_name: str, index: int):
        if self.tileExists(tileset_name, index):
            return self.layers[tileset_name]['tiles'][index]
        return None
    
    def updateTile(self, tileset_name: str, index: int, tile: list):
        if self.tileExists(tileset_name, index):
            for i in range(len(self.layers[tileset_name]['tiles'][index])):
                self.layers[tileset_name]['tiles'][index][i] = tile[i]
        self.buildPositionIndexMap()

    def removeTile(self, tileset_name: str, index: int):
        if self.tileExists(tileset_name, index):
            tile = self.layers[tileset_name]['tiles'].pop(index)
            self.buildPositionIndexMap()
            return tile
        return None
    
    def _modifyImgPath(self, layer:dict):
        """Private method to modify the image path."""
        _layer = layer.copy()
        file = str(_layer['tileset']).split('/')[-1]
        path = f'/images/jportfolio/tilemaps/{file}'
        _layer['tileset'] = path
        return _layer
    
    def length(self):
        """Returns the length of layers"""
        return len(self.order)

    def getJson(self):
        """Return the class data in JSON format."""
        layers = [{
            'name': 'base',
            'tileset': self.base_tile_src,
            'tile_width': self.base_tile_src_w,
            'tile_height': self.base_tile_src_h,
            'z': 0,
            'tiles': [[self.base_tile_src_x, self.base_tile_src_y, self.base_tile_src_w, self.base_tile_src_h]]
        }]

        modified_layers = copy.deepcopy(self.layers)
        overlay_layers =  copy.deepcopy(self.layers)

        for layer in reversed(self.order):
            tiles = []
            overlay_tiles = []
            for tile in self.layers[layer]['tiles']:
                if tile[5] == 1:
                    overlay_tiles.append(tile)
                else:
                    tiles.append(tile)
            modified_layers[layer]['tiles'] = tiles
            overlay_layers[layer]['tiles'] = overlay_tiles
        
        layers.extend([self._modifyImgPath(modified_layers[layer]) for layer in self.order])

        layers_json = json.dumps({
            'name': self.name,
            'world_size': {'width': self.world_size_width, 'height': self.world_size_height},
            'weather': self.weather,
            'start_position': {'x': self.start_position_x, 'y': self.start_position_y},
            'doors': self.doors,
            'layers': layers
        }, indent=2)

        overlay_json = json.dumps({
            'name': self.name + ' Overlay',
            'world_size': {'width': self.world_size_width, 'height': self.world_size_height},
            'layers': overlay_layers

        }, indent=2)

        return layers_json, overlay_json 
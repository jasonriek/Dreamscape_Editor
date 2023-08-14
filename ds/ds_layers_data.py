import copy
import json
from PySide6.QtGui import (QPainter, QPixmap)


class LayersData:
    def __init__(self, parent=None):
        self.parent = parent

        # Layer Attributes
        self.active_layer_src = ''
        self.active_layer_name = ''
        self._layers = {}
        self.order = []
        self.layer_visibility = []
        self.pixmaps = []
        self.base_pixmap = None
        self.position_to_index_map = {}
        self.setting_tileset = False

        # Base Tile Attributes
        self.base_tiles_visible = True
        self.base_tile_src = ''
        self.base_tile_src_x = 0
        self.base_tile_src_y = 0
        self.base_tile_src_w = 32
        self.base_tile_src_h = 32

        # Initialize position index map
        self.buildPositionIndexMap()

    def __getitem__(self, key):
        return self._layers[key]

    def __setitem__(self, key, value):
        self._layers[key] = value

    def __delitem__(self, key):
        del self._layers[key]

    def __contains__(self, key):
        return key in self._layers

    def __iter__(self):
        return iter(self._layers)

    def __len__(self):
        return self.length()

    def __repr__(self):
        return repr(self._layers)
    
    def __deepcopy__(self, memo):
        cls = self.__class__
        new_obj = cls.__new__(cls)
        memo[id(self)] = new_obj

        # Manually deep copy simple attributes
        for attr, value in self.__dict__.items():
            if attr not in ['pixmaps', 'base_pixmap']:
                setattr(new_obj, attr, copy.deepcopy(value, memo))

        # Clone the pixmaps in layer_pixmaps
        new_obj.pixmaps = [self._clone_pixmap(pixmap) for pixmap in self.pixmaps]

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
        for layer_name, layer_data in self._layers.items():
            pos_map = {}
            for i, tile in enumerate(layer_data['tiles']):
                x, y = tile[2], tile[3]
                pos_map[(x, y)] = i
            self.position_to_index_map[layer_name] = pos_map

    def getTileIndexFromXY(self, x, y):
            """Retrieve tile index from x,y coordinates."""
            return self.position_to_index_map.get(self.active_layer_name, {}).get((x, y))

    def getActiveLayerIndex(self):
        if self.active_layer_name in self.order:
            return self.order.index(self.active_layer_name)
        return None

    def getPathByLayerName(self, layer_name:str):
        for layer in self._layers.values():
            if layer['name'] == layer_name:
                return layer['tileset']
        return None

    def changeVisibility(self, state:bool):
        '''Change the selected layer's visibility'''
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
            return index >= 0 and index < len(self._layers[tileset_name]['tiles'])
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
            self._layers[tileset_name] = {
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
        return self._layers.get(tileset_name)
    
    def layerIndex(self, tileset_name: str):
        if tileset_name in self.order:
            return self.order.index(tileset_name)
        return None

    def updateTilesetLayer(self, tileset_name: str, src: str, tile_w: int, tile_h: int, tiles: list, z=0):
        if tileset_name in self.order:
            self._layers[tileset_name]['name'] = tileset_name
            self._layers[tileset_name]['tileset'] = src
            self._layers[tileset_name]['tile_width'] = tile_w
            self._layers[tileset_name]['tile_height'] = tile_h
            self._layers[tileset_name]['tiles'] = tiles
            self._layers[tileset_name]['z'] = z

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
        for layer in self._layers.values():
            if layer['tileset'] == tileset_path:
                count += 1
        return count == 1

    def onlyLayerWithTileset(self, layer_name):
        count = 0
        tileset = self._layers[layer_name]['tileset']
        for layer in self._layers.values():
            if layer['tileset'] == tileset:
                count += 1
        return count == 1
    
    def indexOfFirstTilesetWithPath(self, tileset_path):
        for i, layer in enumerate(self.order):
            if self._layers[layer]['tileset'] == tileset_path:
                return i
        return None

    def removeTilesetLayerAtIndex(self, index:int):
        if index >= 0 and index < len(self.order):
            tileset_name = self.order.pop(index)
            visible = self.layer_visibility.pop(index)
            pixmap = self.pixmaps.pop(index)
            layer = self._layers.pop(tileset_name)
            self.buildPositionIndexMap()
            return layer
        return None
    
    def appendTile(self, tileset_name: str, src_x: int, src_y: int, x: int, y: int, b=0, overlay=0):
        if self._layers.get(tileset_name):
            self._layers[tileset_name]['tiles'].append([
                src_x,
                src_y,
                x,
                y,
                b,
                overlay
            ])
            self.buildPositionIndexMap()
            return len(self._layers[tileset_name]['tiles']) - 1
        return None
    
    def tile(self, tileset_name: str, index: int):
        if self.tileExists(tileset_name, index):
            return self._layers[tileset_name]['tiles'][index]
        return None
    
    def updateTile(self, tileset_name: str, index: int, tile: list):
        if self.tileExists(tileset_name, index):
            for i in range(len(self._layers[tileset_name]['tiles'][index])):
                self._layers[tileset_name]['tiles'][index][i] = tile[i]
        self.buildPositionIndexMap()

    def removeTile(self, tileset_name: str, index: int):
        if self.tileExists(tileset_name, index):
            tile = self._layers[tileset_name]['tiles'].pop(index)
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
        base_src = self.base_tile_src.split('/')[-1]
        base_path = f'/images/jportfolio/tilemaps/{base_src}'
        layers = [{
            'name': 'base',
            'tileset': base_path,
            'tile_width': self.base_tile_src_w,
            'tile_height': self.base_tile_src_h,
            'z': 0,
            'tiles': [[self.base_tile_src_x, self.base_tile_src_y, self.base_tile_src_w, self.base_tile_src_h]]
        }]

        modified_layers = copy.deepcopy(self._layers)
        overlay_layers =  copy.deepcopy(self._layers)

        for layer in self.order:
            tiles = []
            overlay_tiles = []
            for tile in self._layers[layer]['tiles']:
                if tile[5] == 1:
                    overlay_tiles.append(tile)
                else:
                    tiles.append(tile)
            modified_layers[layer]['tiles'] = tiles
            overlay_layers[layer]['tiles'] = overlay_tiles
        
        order = [layer for layer in reversed(self.order)]
        overlay_layers = [self._modifyImgPath(overlay_layers[layer]) for layer in order]
        layers.extend([self._modifyImgPath(modified_layers[layer]) for layer in order])

        layers_json = json.dumps({
            'name': self.parent.world.name,
            'world_size': {'width': self.parent.world.width, 'height': self.parent.world.height},
            'weather': self.parent.world.weather,
            'start_position': {'x': self.parent.world.player_start_position_x, 'y': self.parent.world.player_start_position_y},
            'doors': self.self.parent.world.doors,
            'layers': layers
        }, indent=1)

        overlay_json = json.dumps({
            'name': self.parent.world.name + ' Overlay',
            'world_size': {'width': self.parent.world.width, 'height': self.parent.world.height},
            'layers': overlay_layers

        }, indent=1)

        return layers_json, overlay_json
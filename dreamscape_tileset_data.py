import json

class TilesetLayers:
    def __init__(self):
        self.active_layer_path = ''
        self.active_layer_name = ''
        self.selected_x = 0
        self.selected_y = 0
        self.layers = {}
        self.order = []
        self.layer_visibilty = []
        self.world_size_width = 150
        self.world_size_height = 150
        self.weather = True
        self.start_position_x = 0
        self.start_position_y = 0
        self.name = "World"
        self.base_tile_src = ""
        self.base_tile_src_x = 0
        self.base_tile_src_y = 0
        self.base_tile_src_w = 32
        self.base_tile_src_h = 32
        self.doors = []
        self.layer_pixmaps = []
    
    def getActiveLayerIndex(self):
        if self.active_layer_name in self.order:
            return self.order.index(self.active_layer_name)
        return None

    def getPathByLayerName(self, layer_name:str):
        for layer in self.layers.values():
            if layer['name'] == layer_name:
                return layer['tileset']
        return None

    def changeVisibility(self, state):
        index = self.layerIndex(self.active_layer_name)
        self.layer_visibilty[index] = state

    def getLayerNameByIndex(self, index:str):
        if index >= 0 and index < len(self.order):
            return self.order[index]
        return None
    
    def tilesetNameExists(self, name: int):
        return (name in self.order)
    
    def tileExists(self, tileset_name:str, index:int):
        if self.tilesetNameExists(tileset_name):
            return index >= 0 and index < len(self.layers[tileset_name]['tiles'])
    
    def layerNameExists(self, layer_name: str):
        layer_name = layer_name.lower()
        for name in self.order:
            if name.lower() == layer_name:
                return True
        return False
            
    def appendTilesetLayer(self, tileset_name: str, src: str, tile_w: int, tile_h: int, tiles=None, z=0):
        if tiles is None:
            tiles = []
        if tileset_name not in self.order:
            self.order.append(tileset_name)
            self.layer_visibilty.append(True)
            self.layers[tileset_name] = {
                'name': tileset_name,
                'tileset': src,
                'tile_width': tile_w,
                'tile_height': tile_h,
                'z': z,
                'tiles': tiles   
            }
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
            self.layer_visibilty[layer_1_index], self.layer_visibilty[layer_2_index] = self.layer_visibilty[layer_2_index], self.layer_visibilty[layer_1_index]
            self.layer_pixmaps[layer_1_index], self.layer_pixmaps[layer_2_index] = self.layer_pixmaps[layer_2_index], self.layer_pixmaps[layer_1_index]
            return True
        return False
    
    def onlyLayerWithTileset(self, layer_name):
        count = 0
        tileset = self.layers[layer_name]['tileset']
        for layer in self.layers.values():
            if layer['tileset'] == tileset:
                count += 1
        return (count == 1)
    
    def indexOfFirstTilesetWithPath(self, tileset_path):
        for i, layer in enumerate(self.layers.values()):
            if layer['tileset'] == tileset_path:
                return i
        return None

    def removeTilesetLayerAtIndex(self, index:int):
        if index >= 0 and index < len(self.order):
            tileset_name = self.order.pop(index)
            visible = self.layer_visibilty.pop(index)
            pixmap = self.layer_pixmaps.pop(index)
            return self.layers.pop(tileset_name)
        return None
    
    def appendTile(self, tileset_name: str, src_x: int, src_y: int, x: int, y: int, b=0):
        if self.layers.get(tileset_name):
            self.layers[tileset_name]['tiles'].append([
                src_x,
                src_y,
                x,
                y,
                b
            ])
            
            return len(self.layers[tileset_name]['tiles']) - 1
        return None
    
    def tile(self, tileset_name: str, index: int):
        if self.tileExists(tileset_name, index):
            return self.layers[tileset_name]['tiles'][index]
        return None
    
    def getTileIndexFromXY(self, x, y):
        layer_index = self.layerIndex(self.active_layer_name)
        for i, tile in enumerate(self.layers[self.order[layer_index]]['tiles']):
            if(tile[2] == x and tile[3] == y):
                return i
        return None

    
    def updateTile(self, tileset_name: str, index: int, tile: list):
        if self.tileExists(tileset_name, index):
            for i in range(len(self.layers[tileset_name]['tiles'][index])):
                self.layers[tileset_name]['tiles'][index][i] = tile[i]

    def removeTile(self, tileset_name: str, index: int):
        if self.tileExists(tileset_name, index):
            return self.layers[tileset_name]['tiles'].pop(index)
        return None
    
    def modifyImgPath(self, layer):
        path = f'/images/jportfolio/tilemaps/{layer["tileset"]}'
        layer['tileset'] = path
        return layer
    
    def length(self):
        return len(self.order)

    def getJson(self):
        layers = [{
            'name': 'base',
            'tileset': self.base_tile_src,
            'tile_width': self.base_tile_src_w,
            'tile_height': self.base_tile_src_h,
            'z': 0,
            'tiles': [[self.base_tile_src_x, self.base_tile_src_y, self.base_tile_src_w, self.base_tile_src_h]]
        }]
        layers.extend([self.modifyImgPath(self.layers[layer]) for layer in self.order])
        return json.dumps({
            'name': self.name,
            'world_size': {'width': self.world_size_width, 'height': self.world_size_height},
            'weather': self.weather,
            'start_position': {'x': self.start_position_x, 'y': self.start_position_y},
            'doors': self.doors,
            'layers': layers
        }, indent=4)
    
    def checkMemoryLocations(self):
        for key, layer in self.layers.items():
            print(f"{key} tiles list memory address:", id(layer['tiles']))
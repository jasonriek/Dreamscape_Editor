from PySide6.QtWidgets import (QWidget, QSizePolicy, QScrollArea)
from PySide6.QtGui import (QPainter, QPixmap, QColor, QMouseEvent, QImage, QBrush)
from PySide6.QtCore import (Qt, Signal, QRect, QTimer)
import copy

import ds


class TileCanvas(QWidget):
    tileDropperClicked = Signal(int, int)
    tileDropperReleased = Signal(int, int)
    tileSelected = Signal(list)
    mouseMoved = Signal(int, int)
    undoClicked = Signal(bool)
    redoClicked = Signal(bool)
    initUndo = Signal(bool)
    def __init__(self, tileset_tab_bar, scroll_area:QScrollArea):
        super().__init__()
        self.setMouseTracking(True)
        self.tile_selector = tileset_tab_bar.tile_selector
        self.scroll_area = scroll_area
        self.setFixedSize(ds.data.world.displayWidth(), ds.data.world.displayHeight())
        self.show_grid = True
        self.show_tile_collisons = True
        self.show_tile_overlays = True
        self.is_drawing =  False
        self.is_erasing = False
        self.start_drag_point = None
        self.last_drag_point = None # Store the last drag point to avoid redrawing the same tiles
        self.start_drag_x = 0
        self.start_drag_y = 0
        self.cursor_x = 0
        self.cursor_y = 0
        self.selected_x = 0
        self.selected_y = 0
        self.cursor_tile = None
        self.drag_rectangle = None
        self.selected_tile = None
        self.bucket_debounce_timer = QTimer(self)
        self.bucket_debounce_timer.setSingleShot(True)
        self.bucket_debounce_timer.timeout.connect(self.resetBucketFillingFlag)
        self.action_history = []
        self.bucket_filling = False
        self.fill_x_start = 0
        self.fill_y_start = 0
        self.fill_x_end = 0
        self.fill_y_end = 0
        self.undo_started = False
        self.action_index = -1
        self.saveState()

        ds.data.layers.pixmaps = [
            QPixmap(ds.data.world.displayWidth(), ds.data.world.displayHeight()) for _ in range(len(ds.data.layers))]
        for pixmap in ds.data.layers.pixmaps:
            pixmap.fill(Qt.GlobalColor.transparent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def saveState(self):
        state = copy.deepcopy(ds.data)
        
        # Remove states after current action_index (if any)
        self.action_history = self.action_history[:self.action_index+1]

        # Add the new state and update action_index
        self.action_history.append(state)
        self.action_index += 1

        print("After saveState, action_index:", self.action_index, "History length:", len(self.action_history))
        
        if not self.undo_started:
            self.initUndo.emit(True)
            self.undo_started = True

        # If history is too long, remove the oldest action
        if len(self.action_history) > ds.data.MAX_HISTORY_SIZE:
            self.action_history.pop(0)
            self.action_index -= 1  # Adjust the action index since we removed an item

        self.undoClicked.emit(self.action_index > 0)
        self.redoClicked.emit(self.action_index < (len(self.action_history) - 1))

    def undo(self):
        if self.action_index > 0:
            self.action_index -= 1
            ds.data = copy.deepcopy(self.action_history[self.action_index])
            self.update()  # Redraw the canvas
            self.redrawWorld()
            print("After undo, action_index:", self.action_index)
            self.undoClicked.emit(self.action_index > 0)
            self.redoClicked.emit(self.action_index < (len(self.action_history) - 1))

    def redo(self):
        if self.action_index < len(self.action_history) - 1:
            self.action_index += 1
            ds.data = copy.deepcopy(self.action_history[self.action_index])
            self.update()  # Redraw the canvas
            self.redrawWorld()
            print("After redo, action_index:", self.action_index)
            self.redoClicked.emit(self.action_index < (len(self.action_history) - 1))
            self.undoClicked.emit(self.action_index > 0)

    def resetBucketFillingFlag(self):
        self.bucket_filling = False

    def toggleGrid(self, state):
        self.show_grid = bool(state)
        self.update()
    
    def toggleShowTileCollisons(self, state):
        self.show_tile_collisons = bool(state)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Paint the base tiles first
        if ds.data.layers.base_pixmap and ds.data.layers.base_tiles_visible:
            painter.drawPixmap(0, 0, ds.data.layers.base_pixmap)

        # Paint tiles from all layers based on visibility
        for layer_index in reversed(range(len(ds.data.layers.pixmaps))):
            pixmap = ds.data.layers.pixmaps[layer_index]
            if ds.data.layers.layer_visibility[layer_index]:  # Check if this layer should be rendered
                painter.drawPixmap(0, 0, pixmap)

        # Draw the grid if the flag is set
        if self.show_grid:
            painter.setPen(Qt.GlobalColor.black)
            for x in range(0, ds.data.world.displayWidth(), ds.data.TILE_SIZE):
                painter.drawLine(x, 0, x, ds.data.world.displayHeight())
            for y in range(0, ds.data.world.displayHeight(), ds.data.TILE_SIZE):
                painter.drawLine(0, y, ds.data.world.displayWidth(), y)

        if self.drag_rectangle:
            painter.setBrush(QColor(0, 255, 0, 127))  # Semi-transparent green
            painter.drawRect(self.drag_rectangle)
        
        # Draw the tile under the cursor
        if self.cursor_tile is not None:
            if ds.data.paint_tools.isDrawingTool():
                if ds.data.paint_tools.selection == ds.data.paint_tools.BRUSH:
                    painter.drawImage(self.cursor_x * ds.data.TILE_SIZE, 
                                self.cursor_y * ds.data.TILE_SIZE,
                                self.tile_selector.selected_tiles_pixmap)    
                else:
                    painter.drawImage(self.cursor_x * ds.data.TILE_SIZE, 
                                self.cursor_y * ds.data.TILE_SIZE,
                                self.tile_selector.selected_tile_pixmap)
                
        if ds.data.paint_tools.selection == ds.data.paint_tools.SELECT:
            painter.setPen(QColor(0, 255, 0, 200))  # Semi-transparent green
            painter.drawRect(
                self.cursor_x * ds.data.TILE_SIZE, 
                self.cursor_y * ds.data.TILE_SIZE, 
                ds.data.TILE_SIZE, 
                ds.data.TILE_SIZE
            )

        # Draw a semi-transparent blue square for overlay tiles
        if self.show_tile_overlays:
            overlay_brush = QBrush(QColor(0, 0, 255, 75)) # Semi-transparent blue
            for layer_index in range(len(ds.data.layers.pixmaps)):
                if ds.data.layers.layer_visibility[layer_index]:  # Check if this layer should be rendered
                    for tile_data in ds.data.layers.tilesetLayer(ds.data.layers.order[layer_index])['tiles']:
                        _, _, x, y, b, overlay = tile_data
                        if overlay == 1:
                            painter.fillRect(
                                x * ds.data.TILE_SIZE, 
                                y * ds.data.TILE_SIZE, 
                                ds.data.TILE_SIZE, 
                                ds.data.TILE_SIZE, 
                                overlay_brush
                            )         

        # Draw a semi-transparent red square for barrier tiles
        if self.show_tile_collisons:
            barrier_brush = QBrush(QColor(255, 0, 0, 75))  # Semi-transparent red
            for layer_index in range(len(ds.data.layers.pixmaps)):
                if ds.data.layers.layer_visibility[layer_index]:  # Check if this layer should be rendered
                    for tile_data in ds.data.layers.tilesetLayer(ds.data.layers.order[layer_index])['tiles']:
                        _, _, x, y, b, overlay = tile_data
                        if b == 1:
                            painter.fillRect(x * ds.data.TILE_SIZE, 
                                             y * ds.data.TILE_SIZE, 
                                             ds.data.TILE_SIZE, 
                                             ds.data.TILE_SIZE, 
                                             barrier_brush
                            )
        
        if ds.data.paint_tools.selection == ds.data.paint_tools.SELECT and self.selected_tile:
            painter.setBrush(QColor(0, 255, 0, 75))  # Semi-transparent green
            painter.drawRect(
                self.selected_tile[2] * ds.data.TILE_SIZE, 
                self.selected_tile[3] * ds.data.TILE_SIZE, 
                ds.data.TILE_SIZE, 
                ds.data.TILE_SIZE
            )
                
        painter.end()
    
    def drawBaseTiles(self):
        if not ds.data.layers.base_tile_src:
            return

        # Check if we already have the pixmap, and if not, create it.
        if not ds.data.layers.base_pixmap:
            ds.data.layers.base_pixmap = QPixmap(ds.data.world.displayWidth(), ds.data.world.displayHeight())

        base_tile_img = QImage(ds.data.layers.base_tile_src)
        
        if base_tile_img.isNull():
            print("The base tile image couldn't be loaded!")
            return

        painter = QPainter(ds.data.layers.base_pixmap)

        tile_width = ds.data.layers.base_tile_src_w
        tile_height = ds.data.layers.base_tile_src_h

        src_x = ds.data.layers.base_tile_src_x * tile_width
        src_y = ds.data.layers.base_tile_src_y * tile_height

        # Draw the base tile repeatedly over the entire canvas
        for x in range(0, ds.data.world.displayWidth(), tile_width):
            for y in range(0, ds.data.world.displayHeight(), tile_height):
                painter.drawImage(x, y, base_tile_img, src_x, src_y, tile_width, tile_height)

        painter.end()
    
    def drawTileOnLayer(self, tileset_name, tile_index):
        tile_data = ds.data.layers.tile(tileset_name, tile_index)
        if tile_data:
            src_x, src_y, x, y, b, overlay = tile_data
            tileset_info = ds.data.layers.tilesetLayer(tileset_name)
            tileset_img = QImage(tileset_info['tileset'])
            painter = QPainter(ds.data.layers.pixmaps[ds.data.layers.layerIndex(tileset_name)])  # Assuming you have one QPixmap per tileset layer
            painter.drawImage(x * tileset_info['tile_width'], y * tileset_info['tile_height'],
                      tileset_img,
                      src_x * tileset_info['tile_width'], src_y * tileset_info['tile_height'],
                      tileset_info['tile_width'], tileset_info['tile_height'])
            painter.end()  # End painting

    def redrawWorld(self):
        for tileset_name in ds.data.layers.order:
            self.redrawLayer(tileset_name)

    def redrawLayer(self, tileset_name):
        tileset_info = ds.data.layers.tilesetLayer(tileset_name)
        tileset_img = QImage(tileset_info['tileset'])
        
        pixmap = QPixmap(ds.data.world.displayWidth(), ds.data.world.displayHeight())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        
        for tile_data in tileset_info['tiles']:
            src_x, src_y, x, y, b, overlay = tile_data
            painter.drawImage(x * ds.data.TILE_SIZE, y * ds.data.TILE_SIZE,
                            tileset_img,
                            src_x * tileset_info['tile_width'], src_y * tileset_info['tile_height'],
                            tileset_info['tile_width'], tileset_info['tile_height'])
        if len(ds.data.layers.pixmaps):
            ds.data.layers.pixmaps[ds.data.layers.layerIndex(tileset_name)] = pixmap
        else:
            ds.data.layers.pixmaps.append(pixmap)
        
        painter.end()  # End painting

    def resizeCanvas(self, width, height):
        self.setFixedSize(width, height)
        # Resize underlying QPixmaps to the new dimensions
        ds.data.layers.pixmaps = [QPixmap(width, height) for _ in range(len(ds.data.layers))]
        for pixmap in ds.data.layers.pixmaps:
            pixmap.fill(Qt.GlobalColor.transparent)
        self.redrawWorld()  # Redraw all tiles

    def swapLayers(self, layer1_index, layer2_index):
        # Swap the tilesets in TilesetLayers
        success = ds.data.layers.swapLayerOrder(layer1_index, layer2_index)
        if not success:
            print(f"Failed to swap layers: {layer1_index} and {layer2_index}")
            return

        # Redraw every layer to ensure correct stacking order
        for tileset_name in ds.data.layers.order:
            self.redrawLayer(tileset_name)
        self.update()  # Trigger a repaint

    def paintBrushTileAt(self, x, y):
        try:
            tiles = self.tile_selector.getSelectedTiles()
            first_tile_x = tiles[0][0]
            first_tile_y = tiles[0][1]
            org_x = x
            org_y = y
            for tile in tiles:
                x = org_x + abs(first_tile_x - tile[0])
                y = org_y + abs(first_tile_y - tile[1])
                self.paintTileAt(x, y, tile[0], tile[1])
                print(x, y, tile[0], tile[1])
        except Exception as error:
            print(f'paintBrushTileAt({x}, {y}) Error: {str(error)}')

    def setTileCollision(self, state):
        if state:
            state = 1
        ds.data.world.barrier = int(state)
        tile_index = ds.data.layers.getTileIndexFromXY(self.selected_x, self.selected_y)
        tile = self.getTile(self.selected_x, self.selected_y)
        if tile:
            tile[4] = state
            ds.data.layers.updateTile(ds.data.layers.active_layer_name, tile_index, tile)
            self.update()

    def setTileOverlay(self, state):
        if state:
            state = 1
        ds.data.world.overylay = int(state)
        tile_index = ds.data.layers.getTileIndexFromXY(self.selected_x, self.selected_y)
        tile = self.getTile(self.selected_x, self.selected_y)
        if tile:
            tile[5] = state
            ds.data.layers.updateTile(ds.data.layers.active_layer_name, tile_index, tile)

    def paintTileAt(self, x, y, src_x=None, src_y=None):
        tileselector_x = ds.data.world.selected_tile_x
        tileselector_y = ds.data.world.selected_tile_y
        if src_x is not None and src_y is not None:
            tileselector_x = src_x
            tileselector_y = src_y
        
        if x < 0 or x >= ds.data.world.width or y < 0 or y >= ds.data.world.height:
            return

        # Check if tile already exists here at this layer, if so, replace it.
        current_layer_index = ds.data.layers.layerIndex(ds.data.layers.active_layer_name)
        tile_index = ds.data.layers.getTileIndexFromXY(x, y)
        if tile_index is not None and tile_index >= 0: # update the current tile
            ds.data.layers.updateTile(ds.data.layers.active_layer_name, tile_index,
                [tileselector_x,
                tileselector_y,
                x,
                y,
                ds.data.world.barrier,
                ds.data.world.overylay]
            )
            # Redraw every layer to ensure correct stacking order
            #for tileset_name in dsc.tileset_layers.order:
            #    self.redraw_layer(tileset_name)
        else: # make a new tile
            tile_index = ds.data.layers.appendTile(
                ds.data.layers.active_layer_name, 
                tileselector_x, 
                tileselector_y,
                x,
                y,
                ds.data.world.barrier)
        if current_layer_index is not None:
            # Register the tile drawing as an operation for the selected layer
            self.drawTileOnLayer(ds.data.layers.active_layer_name, tile_index)
            self.update()  # Trigger a repaint

    def paintTile(self, event:QMouseEvent):
        if not self.tile_selector.getSelectedTile():
            return
        
        x = int(event.position().x()) // ds.data.TILE_SIZE
        y = int(event.position().y()) // ds.data.TILE_SIZE
        self.paintTileAt(x, y)
   
    def eraseTileAt(self, x, y):
        if x < 0 or x >= ds.data.world.width or y < 0 or y >= ds.data.world.height:
            return
        # Check if tile already exists here at this layer, if so, replace it.
        current_layer_index = ds.data.layers.layerIndex(ds.data.layers.active_layer_name)
        tile_index = ds.data.layers.getTileIndexFromXY(x, y)
        if tile_index is not None and tile_index >= 0: # update the current tile
            tile = ds.data.layers.removeTile(ds.data.layers.active_layer_name, tile_index)
            if tile == self.selected_tile:
                self.selected_tile = None
            print(f"{tile} tile removed.")

            if current_layer_index is not None:
                self.update()  # Trigger a repaint
        else:
            print('Nothing here to erase.')

    def eraseTile(self, event:QMouseEvent):
        x = int(event.position().x()) // ds.data.TILE_SIZE
        y = int(event.position().y()) // ds.data.TILE_SIZE
        self.eraseTileAt(x, y)
            
    def calculateDragArea(self, event:QMouseEvent):
        """Fill tiles in the rectangular drag area."""
        x = int(event.position().x()) // ds.data.TILE_SIZE
        y = int(event.position().y()) // ds.data.TILE_SIZE
        distance_from_start_x = x - self.start_drag_x
        distance_from_start_y = y - self.start_drag_y

        # Determine the starting and ending points based on drag direction
        self.fill_x_start, self.fill_x_end = (self.start_drag_x, x) if distance_from_start_x >= 0 else (x, self.start_drag_x)
        self.fill_y_start, self.fill_y_end = (self.start_drag_y, y) if distance_from_start_y >= 0 else (y, self.start_drag_y)

        self.drag_rectangle = QRect(
            self.fill_x_start * ds.data.TILE_SIZE,
            self.fill_y_start * ds.data.TILE_SIZE,
            (self.fill_x_end - self.fill_x_start + 1) * ds.data.TILE_SIZE,
            (self.fill_y_end - self.fill_y_start + 1) * ds.data.TILE_SIZE
        )
        self.update()

    def fillDragArea(self):
        for xi in range(self.fill_x_start, self.fill_x_end + 1):  # +1 to include the end position
            for yi in range(self.fill_y_start, self.fill_y_end + 1):
                # Logic to fill a tile at position (xi, yi) goes here.
                self.paintTileAt(xi, yi)  # Assuming you have such a function.
        self.update()
    
    def getTile(self, x, y):
        tile_index = ds.data.layers.getTileIndexFromXY(x, y)
        tile = ds.data.layers.tile(ds.data.layers.active_layer_name, tile_index) if tile_index is not None else None
        return tile
  
    def floodFill(self, x, y, target_tile, replace_tile):
        stack = [(x, y)]
        
        while stack:
            x, y = stack.pop()
            if x < 0 or x >= ds.data.world.width or y < 0 or y >= ds.data.world.height:
                continue

            current_tile_index = ds.data.layers.getTileIndexFromXY(x, y)
            current_tile = ds.data.layers.tile(ds.data.layers.active_layer_name, current_tile_index) if current_tile_index is not None else None
            
            if not current_tile or current_tile[0:2] != target_tile:
                continue
            if current_tile[0:2] == replace_tile:
                continue
            
            self.paintTileAt(x, y)
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])

    def mousePressEvent(self, event: QMouseEvent):
        x = int(event.position().x()) // ds.data.TILE_SIZE
        y = int(event.position().y()) // ds.data.TILE_SIZE
        # Start drawing when left mouse button is pressed
        if event.button() == Qt.MouseButton.LeftButton and not self.bucket_filling:

            paint_tool = ds.data.paint_tools.selection
            
            if paint_tool == ds.data.paint_tools.PENCIL:
                self.is_drawing = True
                self.is_erasing = False
                self.paintTile(event)
                self.saveState()

            elif paint_tool == ds.data.paint_tools.BRUSH:
                self.is_drawing = True
                self.is_erasing = False
                self.paintBrushTileAt(x, y)
                self.saveState()

            elif paint_tool == ds.data.paint_tools.ERASER:
                self.is_drawing = False
                self.is_erasing = True
                self.eraseTile(event)
                self.saveState()

            elif paint_tool == ds.data.paint_tools.DRAG_DRAW:
                self.is_drawing = True
                self.start_drag_x = x
                self.start_drag_y = y
                self.calculateDragArea(event)
                self.paintTile(event)
                self.saveState()

            elif paint_tool == ds.data.paint_tools.DRAG:
                self.start_drag_point = event.position().toPoint()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)

            elif paint_tool == ds.data.paint_tools.BUCKET:
                if self.bucket_filling or self.bucket_debounce_timer.isActive():
                    return
                self.saveState()
                
                self.bucket_filling = True
                print('Bucket filling...')
                try:
                    target_tile = self.getTile(x, y)
                    replace_tile = (ds.data.world.selected_tile_x, ds.data.world.selected_tile_y)
                    if target_tile:
                        self.floodFill(x, y, target_tile[0:2], replace_tile)
                    self.redrawWorld()
                    self.update()  # Redraw canvas after flood fill
                except Exception as error:
                    print(f'Paint Fill Error: {str(error)}')
                finally:
                    self.bucket_debounce_timer.start(1000)  # 1000 ms = 1 second debounce

            elif paint_tool == ds.data.paint_tools.DROPPER:
                target_tile = self.getTile(x, y)
                if target_tile:
                    self.tileDropperClicked.emit(target_tile[0], target_tile[1])
            
            elif paint_tool == ds.data.paint_tools.SELECT:
                self.selected_x = x
                self.selected_y = y
                self.selected_tile = self.getTile(x, y)
                if self.selected_tile is not None:
                    self.tileSelected.emit(self.selected_tile)
                
            event.accept()
        
        elif event.button() == Qt.MouseButton.RightButton and not self.bucket_filling:
            target_tile = self.getTile(x, y)
            if target_tile:
                self.tileDropperClicked.emit(target_tile[0], target_tile[1])
        else:
            event.ignore()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        x = int(event.position().x()) // ds.data.TILE_SIZE
        y = int(event.position().y()) // ds.data.TILE_SIZE
        paint_tool = ds.data.paint_tools.selection
        # Stop drawing when left mouse button is released
        if event.button() == Qt.MouseButton.LeftButton:
            if paint_tool == ds.data.paint_tools.DRAG_DRAW:
                self.fillDragArea()
            elif paint_tool == ds.data.paint_tools.DRAG and self.start_drag_point is not None:
                self.setCursor(Qt.CursorShape.ArrowCursor)  # Reset the cursor
                self.start_drag_point = None  # Reset the dragging state
           
            self.drag_rectangle = None
            self.is_drawing = False
            self.is_erasing = False
            self.update()
            self.redrawWorld()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            target_tile = self.getTile(x, y)
            if target_tile:
                self.tileDropperReleased.emit(target_tile[0], target_tile[1])
        else:
            event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent):
        x = int(event.position().x()) // ds.data.TILE_SIZE
        y = int(event.position().y()) // ds.data.TILE_SIZE
        paint_tool = ds.data.paint_tools.selection
        self.mouseMoved.emit(x, y)
        
        if self.is_drawing and (paint_tool == ds.data.paint_tools.PENCIL):
            self.paintTile(event)
        elif self.is_drawing and paint_tool == ds.data.paint_tools.BRUSH:
            self.paintBrushTileAt(x, y)
        elif self.is_erasing and (paint_tool == ds.data.paint_tools.ERASER):
            self.eraseTile(event)
        elif self.is_drawing and (paint_tool == ds.data.paint_tools.DRAG_DRAW):
            self.calculateDragArea(event)
        elif paint_tool == ds.data.paint_tools.DRAG:
            if self.start_drag_point is not None:  # Check if we started dragging
                # Calculate the distance moved
                delta = event.position().toPoint() - self.start_drag_point  # Convert QPointF to QPoint
                h_scroll_bar = self.scroll_area.horizontalScrollBar()  # Assuming the parent is the QScrollArea
                v_scroll_bar = self.scroll_area.verticalScrollBar()
                h_scroll_bar.setValue(h_scroll_bar.value() - delta.x())
                v_scroll_bar.setValue(v_scroll_bar.value() - delta.y())
                
                # Update the initial position for the next move event
                self.start_drag_point = event.position().toPoint()  # Convert QPointF to QPoint
        
        self.cursor_x = int(event.position().x()) // ds.data.TILE_SIZE
        self.cursor_y = int(event.position().y()) // ds.data.TILE_SIZE
        self.cursor_tile = self.tile_selector.getSelectedTile()  # update the tile under the cursor
        self.update()




from PySide6.QtWidgets import (QWidget, QGraphicsView, QSizePolicy, QTabBar, QVBoxLayout, QScrollArea)
from PySide6.QtGui import (QPainter, QPixmap, QColor, QMouseEvent, QImage, QBrush)
from PySide6.QtCore import (Qt, Signal, QPoint, QRect)

import dreamscape_config

class TileSelector(QWidget):
    tileSelected = Signal(int, int)
    def __init__(self):
        super().__init__()
        self.selected_tile = None
        self.active_tile_widget = None
        self.show_grid = False

    def toggle_grid(self, state=1):
        self.show_grid = bool(state)
        self.update()
    
    def changeTileset(self, name:str, path:str):
        dreamscape_config.tileset_layers.active_layer_name = name
        dreamscape_config.tileset_layers.active_layer_path = path
        self.tileset = QImage(path)
        self.setFixedSize(self.tileset.width(), self.tileset.height())
        self.update()

    def setTileset(self, name:str, path:str):
        dreamscape_config.tileset_layers.appendTilesetLayer(name, path, 32, 32)
        self.changeTileset(name, path)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw checkered background
        for x in range(0, self.width(), dreamscape_config.CHECKER_SIZE):
            for y in range(0, self.height(), dreamscape_config.CHECKER_SIZE):
                if (x // dreamscape_config.CHECKER_SIZE) % 2 == 0:
                    color = dreamscape_config.WHITE if (y // dreamscape_config.CHECKER_SIZE) % 2 == 0 else dreamscape_config.LIGHT_GRAY
                else:
                    color = dreamscape_config.LIGHT_GRAY if (y // dreamscape_config.CHECKER_SIZE) % 2 == 0 else dreamscape_config.WHITE

                painter.fillRect(x, y, dreamscape_config.CHECKER_SIZE, dreamscape_config.CHECKER_SIZE, color)

        painter.drawImage(0, 0, self.tileset)

        # Draw the grid if the flag is set
        if self.show_grid:
            painter.setPen(Qt.GlobalColor.black)
            for x in range(0, self.width(), dreamscape_config.TILE_SIZE):
                painter.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), dreamscape_config.TILE_SIZE):
                painter.drawLine(0, y, self.width(), y)

        if self.selected_tile:
            tile_x, tile_y = self.selected_tile
            painter.setPen(Qt.GlobalColor.red)
            painter.drawRect(tile_x * dreamscape_config.TILE_SIZE, tile_y * dreamscape_config.TILE_SIZE, dreamscape_config.TILE_SIZE, dreamscape_config.TILE_SIZE)

    def selectTile(self, x, y):
        dreamscape_config.tileset_layers.selected_x = x
        dreamscape_config.tileset_layers.selected_y = y
        self.tileSelected.emit(x, y)
        self.selected_tile = (x, y)
        if self.selected_tile:
            tile_x, tile_y = self.selected_tile
            self.selected_tile_pixmap = self.tileset.copy(tile_x * dreamscape_config.TILE_SIZE, 
                                                tile_y * dreamscape_config.TILE_SIZE, 
                                                dreamscape_config.TILE_SIZE, 
                                                dreamscape_config.TILE_SIZE)
                # Assuming you have a reference to the ActiveTileWidget instance
        self.active_tile_widget.update_active_tile_display(self.selected_tile_pixmap)
        self.update()  # Trigger a repaint

    def mousePressEvent(self, event: QMouseEvent):
        x = int(event.position().x()) // dreamscape_config.TILE_SIZE
        y = int(event.position().y()) // dreamscape_config.TILE_SIZE
        self.selectTile(x, y)

    def get_selected_tile(self):
        return self.selected_tile

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
        self.setLayout(layout)

class TilesetBar(QWidget):
    tilesetChanged = Signal(str)
    def __init__(self):
        super().__init__()

        # Create the TileSelector and QTabBar
        self.tileset_scroll_area = TilesetScrollArea()
        self.tile_selector = self.tileset_scroll_area.tile_selector
        self.tab_bar = QTabBar()
        self.tab_bar.setExpanding(False)
        self.tab_bar.setStyleSheet("""
            QTabBar::tab {
                min-width: 100px;
            }
        """)
        # Connect tab change to update function
        self.tab_bar.currentChanged.connect(self.changeTileset)

        # Layout
        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.tab_bar)
        self.layout_.addWidget(self.tileset_scroll_area)
        self.setLayout(self.layout_)

        # Dictionary to store tilesets paths associated with tab indexes
        self.tilesets = {}

        self.addTileset('Cyber Punk 1', 'cyberpunk_1_assets_1.png')
    
    def changeIndexByTilesetPath(self, tileset_path):
        for i in range(self.tab_bar.count()):
            if self.tilesets[i][1] == tileset_path:
                self.tab_bar.setCurrentIndex(i)
                break
    
    def removeTabByTilesetPath(self, tileset_path:str):
        self.tab_bar.setCurrentIndex(0) # Default to the first tab
        for i in range(self.tab_bar.count()):
            if self.tilesets[i][1] == tileset_path:
                self.tab_bar.removeTab(i)
                break

    def addTileset(self, tileset_name:str, tileset_path:str):
        self.tile_selector.setTileset(tileset_name, tileset_path)
        index = self.tab_bar.addTab(tileset_name)
        self.tilesets[index] = (tileset_name, tileset_path)
        # If it's the first tileset, set it immediately
        if self.tab_bar.count() == 1:
            self.changeTileset(0)

    def changeTileset(self, index):
        tileset_data = self.tilesets.get(index)
        if tileset_data:
            self.tile_selector.changeTileset(tileset_data[0], tileset_data[1])
            self.tilesetChanged.emit(tileset_data[1])

class TileCanvas(QWidget):
    tileDropperClicked = Signal(int, int)
    tileSelected = Signal(list)
    mouseMoved = Signal(int, int)
    def __init__(self, tileset_bar, scroll_area:QScrollArea):
        super().__init__()
        self.setMouseTracking(True)
        self.tile_selector = tileset_bar.tile_selector
        self.scroll_area = scroll_area
        self.setFixedSize(dreamscape_config.tileset_layers.displayWidth(), dreamscape_config.tileset_layers.displayHeight())
        self.show_grid = True
        self.show_tile_collisons = True
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
        self.bucket_fill = False
        self.selected_tile = None

        dreamscape_config.tileset_layers.layer_pixmaps = [QPixmap(dreamscape_config.tileset_layers.displayWidth(), dreamscape_config.tileset_layers.displayHeight()) for _ in range(dreamscape_config.tileset_layers.length())]
        for pixmap in dreamscape_config.tileset_layers.layer_pixmaps:
            pixmap.fill(Qt.GlobalColor.transparent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def toggle_grid(self, state):
        self.show_grid = bool(state)
        self.update()
    
    def toggleShowTileCollisons(self, state):
        self.show_tile_collisons = bool(state)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Paint the base tiles first
        if dreamscape_config.tileset_layers.base_pixmap and dreamscape_config.tileset_layers.base_tiles_visible:
            painter.drawPixmap(0, 0, dreamscape_config.tileset_layers.base_pixmap)

        # Paint tiles from all layers based on visibility
        for layer_index in reversed(range(len(dreamscape_config.tileset_layers.layer_pixmaps))):
            pixmap = dreamscape_config.tileset_layers.layer_pixmaps[layer_index]
            if dreamscape_config.tileset_layers.layer_visibility[layer_index]:  # Check if this layer should be rendered
                painter.drawPixmap(0, 0, pixmap)

        # Draw the grid if the flag is set
        if self.show_grid:
            painter.setPen(Qt.GlobalColor.black)
            for x in range(0, dreamscape_config.tileset_layers.displayWidth(), dreamscape_config.TILE_SIZE):
                painter.drawLine(x, 0, x, dreamscape_config.tileset_layers.displayHeight())
            for y in range(0, dreamscape_config.tileset_layers.displayHeight(), dreamscape_config.TILE_SIZE):
                painter.drawLine(0, y, dreamscape_config.tileset_layers.displayWidth(), y)

        if self.drag_rectangle:
            painter.setBrush(QColor(0, 255, 0, 127))  # Semi-transparent green
            painter.drawRect(self.drag_rectangle)
        
        # Draw the tile under the cursor
        if self.cursor_tile is not None:
            if dreamscape_config.paint_tools.isDrawingTool(): 
                painter.drawImage(self.cursor_x * dreamscape_config.TILE_SIZE, 
                                self.cursor_y * dreamscape_config.TILE_SIZE,
                                self.tile_selector.selected_tile_pixmap)
        if dreamscape_config.paint_tools.selection == dreamscape_config.SELECT:
            painter.setPen(QColor(0, 255, 0, 200))  # Semi-transparent green
            painter.drawRect(self.cursor_x * dreamscape_config.TILE_SIZE, self.cursor_y * dreamscape_config.TILE_SIZE, dreamscape_config.TILE_SIZE, dreamscape_config.TILE_SIZE)

        # Draw a semi-transparent red square for barrier tiles
        if self.show_tile_collisons:
            barrier_brush = QBrush(QColor(255, 0, 0, 75))  # Semi-transparent red
            for layer_index in range(len(dreamscape_config.tileset_layers.layer_pixmaps)):
                if dreamscape_config.tileset_layers.layer_visibility[layer_index]:  # Check if this layer should be rendered
                    for tile_data in dreamscape_config.tileset_layers.tilesetLayer(dreamscape_config.tileset_layers.order[layer_index])['tiles']:
                        _, _, x, y, b, overlay = tile_data
                        if b == 1:
                            painter.fillRect(x * dreamscape_config.TILE_SIZE, y * dreamscape_config.TILE_SIZE, dreamscape_config.TILE_SIZE, dreamscape_config.TILE_SIZE, barrier_brush)
        
        if dreamscape_config.paint_tools.selection == dreamscape_config.SELECT and self.selected_tile:
            painter.setBrush(QColor(0, 255, 0, 75))  # Semi-transparent green
            painter.drawRect(self.selected_tile[2] * dreamscape_config.TILE_SIZE, self.selected_tile[3] * dreamscape_config.TILE_SIZE, dreamscape_config.TILE_SIZE, dreamscape_config.TILE_SIZE)
                

        painter.end()
    
    def drawBaseTiles(self):
        if not dreamscape_config.tileset_layers.base_tile_src:
            return

        # Check if we already have the pixmap, and if not, create it.
        if not dreamscape_config.tileset_layers.base_pixmap:
            dreamscape_config.tileset_layers.base_pixmap = QPixmap(dreamscape_config.tileset_layers.displayWidth(), dreamscape_config.tileset_layers.displayHeight())

        base_tile_img = QImage(dreamscape_config.tileset_layers.base_tile_src)
        
        if base_tile_img.isNull():
            print("The base tile image couldn't be loaded!")
            return

        painter = QPainter(dreamscape_config.tileset_layers.base_pixmap)

        tile_w = dreamscape_config.tileset_layers.base_tile_src_w
        tile_h = dreamscape_config.tileset_layers.base_tile_src_h

        src_x = dreamscape_config.tileset_layers.base_tile_src_x * tile_w
        src_y = dreamscape_config.tileset_layers.base_tile_src_y * tile_h

        # Draw the base tile repeatedly over the entire canvas
        for x in range(0, dreamscape_config.tileset_layers.displayWidth(), tile_w):
            for y in range(0, dreamscape_config.tileset_layers.displayHeight(), tile_h):
                painter.drawImage(x, y, base_tile_img, src_x, src_y, tile_w, tile_h)

        painter.end()
    
    def draw_tile_on_layer(self, tileset_name, tile_index):
        tile_data = dreamscape_config.tileset_layers.tile(tileset_name, tile_index)
        if tile_data:
            src_x, src_y, x, y, b, overlay = tile_data
            tileset_info = dreamscape_config.tileset_layers.tilesetLayer(tileset_name)
            tileset_img = QImage(tileset_info['tileset'])
            painter = QPainter(dreamscape_config.tileset_layers.layer_pixmaps[dreamscape_config.tileset_layers.layerIndex(tileset_name)])  # Assuming you have one QPixmap per tileset layer
            painter.drawImage(x * tileset_info['tile_width'], y * tileset_info['tile_height'],
                      tileset_img,
                      src_x * tileset_info['tile_width'], src_y * tileset_info['tile_height'],
                      tileset_info['tile_width'], tileset_info['tile_height'])
            painter.end()  # End painting

    def redraw_world(self):
        for tileset_name in dreamscape_config.tileset_layers.order:
            self.redraw_layer(tileset_name)

    def redraw_layer(self, tileset_name):
        tileset_info = dreamscape_config.tileset_layers.tilesetLayer(tileset_name)
        tileset_img = QImage(tileset_info['tileset'])
        
        pixmap = QPixmap(dreamscape_config.tileset_layers.displayWidth(), dreamscape_config.tileset_layers.displayHeight())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        
        for tile_data in tileset_info['tiles']:
            src_x, src_y, x, y, b, overlay = tile_data
            painter.drawImage(x * dreamscape_config.TILE_SIZE, y * dreamscape_config.TILE_SIZE,
                            tileset_img,
                            src_x * tileset_info['tile_width'], src_y * tileset_info['tile_height'],
                            tileset_info['tile_width'], tileset_info['tile_height'])
        dreamscape_config.tileset_layers.layer_pixmaps[dreamscape_config.tileset_layers.layerIndex(tileset_name)] = pixmap
        painter.end()  # End painting

    def resize_canvas(self, width, height):
        self.setFixedSize(width, height)
        # Resize underlying QPixmaps to the new dimensions
        dreamscape_config.tileset_layers.layer_pixmaps = [QPixmap(width, height) for _ in range(dreamscape_config.tileset_layers.length())]
        for pixmap in dreamscape_config.tileset_layers.layer_pixmaps:
            pixmap.fill(Qt.GlobalColor.transparent)
        self.redraw_world()  # Redraw all tiles

    def swap_layers(self, layer1_index, layer2_index):
        # Swap the tilesets in TilesetLayers
        success = dreamscape_config.tileset_layers.swapLayerOrder(layer1_index, layer2_index)
        if not success:
            print(f"Failed to swap layers: {layer1_index} and {layer2_index}")
            return

        # Redraw every layer to ensure correct stacking order
        for tileset_name in dreamscape_config.tileset_layers.order:
            self.redraw_layer(tileset_name)
        self.update()  # Trigger a repaint

    def paintTileAt(self, x, y):
        if x < 0 or x >= dreamscape_config.tileset_layers.world_size_width or y < 0 or y >= dreamscape_config.tileset_layers.world_size_height:
            return

        # Check if tile already exists here at this layer, if so, replace it.
        current_layer_index = dreamscape_config.tileset_layers.layerIndex(dreamscape_config.tileset_layers.active_layer_name)
        tile_index = dreamscape_config.tileset_layers.getTileIndexFromXY(x, y)
        if tile_index is not None and tile_index >= 0: # update the current tile
            dreamscape_config.tileset_layers.updateTile(dreamscape_config.tileset_layers.active_layer_name, tile_index,
                [dreamscape_config.tileset_layers.selected_x,
                dreamscape_config.tileset_layers.selected_y,
                x,
                y,
                dreamscape_config.tileset_layers.barrier,
                dreamscape_config.tileset_layers.overylay]
            )
            # Redraw every layer to ensure correct stacking order
            #for tileset_name in dreamscape_config.tileset_layers.order:
            #    self.redraw_layer(tileset_name)
        else: # make a new tile
            tile_index = dreamscape_config.tileset_layers.appendTile(
                dreamscape_config.tileset_layers.active_layer_name, 
                dreamscape_config.tileset_layers.selected_x, 
                dreamscape_config.tileset_layers.selected_y,
                x,
                y,
                dreamscape_config.tileset_layers.barrier)
        if current_layer_index is not None:
            # Register the tile drawing as an operation for the selected layer
            self.draw_tile_on_layer(dreamscape_config.tileset_layers.active_layer_name, tile_index)
            self.update()  # Trigger a repaint
    
    def setTileCollision(self, state):
        if state:
            state = 1
        dreamscape_config.tileset_layers.barrier = int(state)
        tile_index = dreamscape_config.tileset_layers.getTileIndexFromXY(self.selected_x, self.selected_y)
        tile = self.getTile(self.selected_x, self.selected_y)
        if tile:
            tile[4] = state
            dreamscape_config.tileset_layers.updateTile(
                dreamscape_config.tileset_layers.active_layer_name, tile_index, tile
            )
            self.update()

    def setTileOverlay(self, state):
        if state:
            state = 1
        dreamscape_config.tileset_layers.overylay = int(state)
        tile_index = dreamscape_config.tileset_layers.getTileIndexFromXY(self.selected_x, self.selected_y)
        tile = self.getTile(self.selected_x, self.selected_y)
        if tile:
            tile[5] = state
            dreamscape_config.tileset_layers.updateTile(
                dreamscape_config.tileset_layers.active_layer_name, tile_index, tile
            )

    def paintTile(self, event:QMouseEvent):
        if not self.tile_selector.get_selected_tile():
            return
        
        x = int(event.position().x()) // dreamscape_config.TILE_SIZE
        y = int(event.position().y()) // dreamscape_config.TILE_SIZE
        self.paintTileAt(x, y)
   
    def eraseTileAt(self, x, y):
        if x < 0 or x >= dreamscape_config.tileset_layers.world_size_width or y < 0 or y >= dreamscape_config.tileset_layers.world_size_height:
            return

        # Check if tile already exists here at this layer, if so, replace it.
        current_layer_index = dreamscape_config.tileset_layers.layerIndex(dreamscape_config.tileset_layers.active_layer_name)
        tile_index = dreamscape_config.tileset_layers.getTileIndexFromXY(x, y)
        if tile_index is not None and tile_index >= 0: # update the current tile
            tile = dreamscape_config.tileset_layers.removeTile(dreamscape_config.tileset_layers.active_layer_name, tile_index)
            if tile == self.selected_tile:
                self.selected_tile = None
            print(f"{tile} tile removed.")
            # Redraw every layer to ensure correct stacking order
            for tileset_name in dreamscape_config.tileset_layers.order:
                self.redraw_layer(tileset_name)

            if current_layer_index is not None:
                self.update()  # Trigger a repaint
        else:
            print('Nothing here to erase.')

    def eraseTile(self, event:QMouseEvent):
        x = int(event.position().x()) // dreamscape_config.TILE_SIZE
        y = int(event.position().y()) // dreamscape_config.TILE_SIZE
        self.eraseTileAt(x, y)
            
    def calculateDragArea(self, event:QMouseEvent):
        """Fill tiles in the rectangular drag area."""
        x = int(event.position().x()) // dreamscape_config.TILE_SIZE
        y = int(event.position().y()) // dreamscape_config.TILE_SIZE
        distance_from_start_x = x - self.start_drag_x
        distance_from_start_y = y - self.start_drag_y

        # Determine the starting and ending points based on drag direction
        self.fill_x_start, self.fill_x_end = (self.start_drag_x, x) if distance_from_start_x >= 0 else (x, self.start_drag_x)
        self.fill_y_start, self.fill_y_end = (self.start_drag_y, y) if distance_from_start_y >= 0 else (y, self.start_drag_y)

        self.drag_rectangle = QRect(
            self.fill_x_start * dreamscape_config.TILE_SIZE,
            self.fill_y_start * dreamscape_config.TILE_SIZE,
            (self.fill_x_end - self.fill_x_start + 1) * dreamscape_config.TILE_SIZE,
            (self.fill_y_end - self.fill_y_start + 1) * dreamscape_config.TILE_SIZE
        )
        self.update()

    def fillDragArea(self):
        for xi in range(self.fill_x_start, self.fill_x_end + 1):  # +1 to include the end position
            for yi in range(self.fill_y_start, self.fill_y_end + 1):
                # Logic to fill a tile at position (xi, yi) goes here.
                self.paintTileAt(xi, yi)  # Assuming you have such a function.
        self.update()
    
    def getTile(self, x, y):
        tile_index = dreamscape_config.tileset_layers.getTileIndexFromXY(x, y)
        tile = dreamscape_config.tileset_layers.tile(dreamscape_config.tileset_layers.active_layer_name, tile_index) if tile_index is not None else None
        return tile
    
    def floodFill(self, x, y, target_tile, replace_tile):
        # Base cases
        if x < 0 or x >= dreamscape_config.tileset_layers.world_size_width or y < 0 or y >= dreamscape_config.tileset_layers.world_size_height:
            return
        current_tile_index = dreamscape_config.tileset_layers.getTileIndexFromXY(x, y)
        current_tile = dreamscape_config.tileset_layers.tile(dreamscape_config.tileset_layers.active_layer_name, current_tile_index) if current_tile_index is not None else None
        if not current_tile or current_tile[0:2] != target_tile:
            return
        if current_tile[0:2] == replace_tile:
            return

        # Replace the current tile with the new tile
        self.paintTileAt(x, y)

        # Recur in all directions
        self.floodFill(x+1, y, target_tile, replace_tile)
        self.floodFill(x-1, y, target_tile, replace_tile)
        self.floodFill(x, y+1, target_tile, replace_tile)
        self.floodFill(x, y-1, target_tile, replace_tile)

    def mousePressEvent(self, event: QMouseEvent):
        # Start drawing when left mouse button is pressed
        if event.button() == Qt.MouseButton.LeftButton:
            x = int(event.position().x()) // dreamscape_config.TILE_SIZE
            y = int(event.position().y()) // dreamscape_config.TILE_SIZE
            paint_tool = dreamscape_config.paint_tools.selection
            if paint_tool == dreamscape_config.PENCIL or paint_tool == dreamscape_config.BRUSH:
                self.is_drawing = True
                self.is_erasing = False
                self.paintTile(event)
            elif paint_tool == dreamscape_config.ERASER:
                self.is_drawing = False
                self.is_erasing = True
                self.eraseTile(event)
            elif paint_tool == dreamscape_config.DRAG_DRAW:
                self.is_drawing = True
                self.start_drag_x = x
                self.start_drag_y = y
                self.calculateDragArea(event)
                self.paintTile(event)
            elif paint_tool == dreamscape_config.DRAG:
                self.start_drag_point = event.position().toPoint()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            elif paint_tool == dreamscape_config.BUCKET:
                target_tile = self.getTile(x, y)
                replace_tile = (dreamscape_config.tileset_layers.selected_x, dreamscape_config.tileset_layers.selected_y)
                if target_tile:
                    self.floodFill(x, y, target_tile[0:2], replace_tile)
                self.redraw_world()
                self.update()  # Redraw canvas after flood fill

            elif paint_tool == dreamscape_config.DROPPER:
                target_tile = self.getTile(x, y)
                if target_tile:
                    self.tileDropperClicked.emit(target_tile[0], target_tile[1])
            
            elif paint_tool == dreamscape_config.SELECT:
                self.selected_x = x
                self.selected_y = y
                self.selected_tile = self.getTile(x, y)
                if self.selected_tile is not None:
                    self.tileSelected.emit(self.selected_tile)

            event.accept()
        else:
            event.ignore()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        paint_tool = dreamscape_config.paint_tools.selection
        # Stop drawing when left mouse button is released
        if event.button() == Qt.LeftButton:
            if paint_tool == dreamscape_config.DRAG_DRAW:
                self.fillDragArea()
            elif paint_tool == dreamscape_config.DRAG and self.start_drag_point is not None:
                self.setCursor(Qt.ArrowCursor)  # Reset the cursor
                self.start_drag_point = None  # Reset the dragging state
           
            self.drag_rectangle = None
            self.is_drawing = False
            self.is_erasing = False
            self.update()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent):
        x = int(event.position().x()) // dreamscape_config.TILE_SIZE
        y = int(event.position().y()) // dreamscape_config.TILE_SIZE
        paint_tool = dreamscape_config.paint_tools.selection
        self.mouseMoved.emit(x, y)
        
        if self.is_drawing and (paint_tool == dreamscape_config.PENCIL or paint_tool == dreamscape_config.BRUSH):
            self.paintTile(event)
        elif self.is_erasing and (paint_tool == dreamscape_config.ERASER):
            self.eraseTile(event)
        elif self.is_drawing and (paint_tool == dreamscape_config.DRAG_DRAW):
            self.calculateDragArea(event)
        elif paint_tool == dreamscape_config.DRAG:
            if self.start_drag_point is not None:  # Check if we started dragging
                # Calculate the distance moved
                delta = event.position().toPoint() - self.start_drag_point  # Convert QPointF to QPoint
                h_scroll_bar = self.scroll_area.horizontalScrollBar()  # Assuming the parent is the QScrollArea
                v_scroll_bar = self.scroll_area.verticalScrollBar()
                h_scroll_bar.setValue(h_scroll_bar.value() - delta.x())
                v_scroll_bar.setValue(v_scroll_bar.value() - delta.y())
                
                # Update the initial position for the next move event
                self.start_drag_point = event.position().toPoint()  # Convert QPointF to QPoint
        
        self.cursor_x = int(event.position().x()) // dreamscape_config.TILE_SIZE
        self.cursor_y = int(event.position().y()) // dreamscape_config.TILE_SIZE
        self.cursor_tile = self.tile_selector.get_selected_tile()  # update the tile under the cursor
        self.update()

    def update_layer_visibility(self):
        self.update()  # Trigger repaint



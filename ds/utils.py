import pickle
import copy
from PySide6.QtCore import (QBuffer, QByteArray, QIODevice)
from PySide6.QtGui import (QPixmap)

from .ds_data import Data


class Utils:
    @staticmethod
    def pixmapToBytes(pixmap:QPixmap):
        if pixmap is None:
            return None
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        return byte_array.data()
    
    @staticmethod
    def bytesToPixmap(data_bytes):
        if data_bytes is None:
            return data_bytes
        pixmap = QPixmap()
        pixmap.loadFromData(data_bytes, "PNG")
        return pixmap

    @staticmethod
    def saveToFile(data:Data, file_name:str):
        print("Saving: ", len(data.layers.pixmaps))
        _data = copy.deepcopy(data)
        print("Saving: ", len(_data.layers.pixmaps))
        # Convert QPixmaps to bytes
        _data.layers.pixmaps = [Utils.pixmapToBytes(pixmap) for pixmap in _data.layers.pixmaps]
        _data.layers.base_pixmap = Utils.pixmapToBytes(_data.layers.base_pixmap)
            
        with open(file_name, 'wb') as f:
            pickle.dump(_data, f)

    @staticmethod
    def loadFromFile(path:str):
        data = None
        with open(path, 'rb') as f:
            data:Data = pickle.load(f)
            print("Loaded: ", len(data.layers.pixmaps))

        if data.layers:
            # Convert bytes back to QPixmaps
            data.layers.pixmaps = [Utils.bytesToPixmap(pixmap_bytes) for pixmap_bytes in data.layers.pixmaps]
            data.layers.base_pixmap = Utils.bytesToPixmap(data.layers.base_pixmap)

        return data
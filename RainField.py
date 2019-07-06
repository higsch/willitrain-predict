import pickle

coords = {
    'top_right': (7771252, 1075693),
    'bottom_left': (5983984, 126648)
}


class RainField(object):
    def __init__(self, key, timeStamp, npBinary, createdAt):
        self.key = key
        self.timeStamp = timeStamp
        self.npBinary = npBinary
        self.createdAt = createdAt

        self.arr = self._decodeBinary(npBinary)

    def _decodeBinary(self, npBinary):
        return(pickle.loads(npBinary))

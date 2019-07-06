from Prediction import Prediction

coords = {
    'topRight': (7771252, 1075693),
    'bottomLeft': (5983984, 126648)
}


class RainField(object):
  def __init__(self, radars):
    self._radars = radars
    self._predictions = []
  

  def addLayer(self, radar):
    self._radars.append(radar)
    pass


  def showGraph(self):
    pass
  

  def predict(self, target=10):
    return(Prediction(None))

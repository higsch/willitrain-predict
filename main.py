from downloadRadars import downloadRadars
from RainField import RainField


if __name__ == '__main__':
  # get the last 10 radars
  radars = downloadRadars(24)

  # feed the radars into a rainfield object
  rainField = RainField(radars)

  # show the generated graph
  rainField.showGraph()

  # make a prediction
  prediction = rainField.predict(target=10)

  # extract prediction for a specific location
  predictionAtLoc = prediction.get(location=None)

  print(predictionAtLoc)

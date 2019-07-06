import requests
import json
from datetime import datetime
from io import BytesIO
from uuid import uuid4
from osgeo import gdal
import numpy as np
from skimage import measure
import matplotlib.pyplot as plt
import pickle

API_URL = 'https://opendata-download-radar.smhi.se/api/version/latest/area/sweden/product/comp/'
DATE = datetime.utcnow().strftime('%Y/%m/%d')
FORMAT = 'format=tif'
TIMEZONE = 'timeZone=UTC'
DATETIME_FORMAT = '%Y-%m-%d %H:%M'
IMAGES_FILEPATH = 'radars/images/'
PICKLES_FILEPATH = 'radars/pickles/'


def _fetchRadarInfo():
  url = API_URL + DATE + '?' + FORMAT + '&' + TIMEZONE
  try:
    return(json.loads(requests.get(url).content))
  except IOError as e:
    print(e)


def _parseRadarInfo(radarInfo, maxEntries = 10):
  i = 0
  for entry in radarInfo['files'][::-1]:
    if (i == maxEntries):
      break
    key = entry['key']
    # timeStamp uses UTC
    timeStamp = datetime.strptime(entry['valid'], DATETIME_FORMAT)
    for format in entry['formats']:
      if (format['key'] == 'tif'):
        link = format['link']
        break
    i += 1
    yield (key, timeStamp, link)


def _saveToTiff(name, data):
  with open(IMAGES_FILEPATH + name + '.tiff', 'wb') as handle:
    handle.write(data)


def _getImageArray(image):
  mmapName = '/vsimem/' + str(uuid4())
  gdal.FileFromMemBuffer(mmapName, image.read())
  dataset = gdal.Open(mmapName)
  imageArray = dataset.GetRasterBand(1).ReadAsArray()
  gdal.Unlink(mmapName)
  return(imageArray)


def _saveRainMassesToPng(name, data):
  plt.figure(figsize=(10, 15))
  plt.imshow(data)
  plt.savefig(IMAGES_FILEPATH + name + '.png')
  plt.close()


def _saveToPickle(name, data):
  with open(PICKLES_FILEPATH + name + '.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def identifyRainMasses(arr):
  arr = (arr != 0) & (arr != 255)
  rainMasses = measure.label(arr, background=0, neighbors=4)
  return(rainMasses)


def downloadRadars(numRadars):
  radars = []
  radarInfo = _fetchRadarInfo()
  for (key, timeStamp, link) in _parseRadarInfo(radarInfo, numRadars):
    data = requests.get(link).content
    fileName = str(timeStamp).replace(':', '-').replace(' ', '-')
    _saveToTiff(fileName, data)
    image = BytesIO(data)
    iArr = _getImageArray(image)
    rainMasses = identifyRainMasses(iArr)
    _saveRainMassesToPng('rainmass' + fileName, rainMasses)
    radar = {
      'key': key,
      'timeStamp': timeStamp,
      'data': data,
      'iArr': iArr,
      'rainMasses': rainMasses,
      'downloadedAt': datetime.utcnow()
    }
    _saveToPickle(fileName, radar)
    radars.append(radar)
  return(radars)


if __name__ == '__main__':
  radars = downloadRadars(10)
  print(str(len(radars)) + ' radars have been downloaded.')

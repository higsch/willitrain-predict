import requests
import json
from datetime import datetime
from io import BytesIO
from uuid import uuid4
from osgeo import gdal
import numpy as np
from skimage import measure
import matplotlib.pyplot as plt

API_URL = 'https://opendata-download-radar.smhi.se/api/version/latest/area/sweden/product/comp/'
DATE = datetime.utcnow().strftime('%Y/%m/%d')
FORMAT = 'format=tif'
TIMEZONE = 'timeZone=UTC'
DATETIME_FORMAT = '%Y-%m-%d %H:%M'


def fetchRadarInfo():
    url = API_URL + DATE + '?' + FORMAT + '&' + TIMEZONE
    try:
        return(json.loads(requests.get(url).content))
    except IOError as e:
        print(e)


def parseRadarInfo(radarInfo, maxEntries = 10):
    i = 0
    for entry in radarInfo['files'][::-1]:
        if (i == maxEntries):
            break
        key = entry['key']
        timeStamp = datetime.strptime(entry['valid'], DATETIME_FORMAT)
        for format in entry['formats']:
            if (format['key'] == 'tif'):
                link = format['link']
                break
        i += 1
        yield (key, timeStamp, link)


def saveToFile(name, data):
    file = open('radars/' + name + '.tiff', 'wb')
    file.write(data)
    file.close()


def getImageArray(image):
    mmapName = '/vsimem/' + str(uuid4())
    gdal.FileFromMemBuffer(mmapName, image.read())
    dataset = gdal.Open(mmapName)
    imageArray = dataset.GetRasterBand(1).ReadAsArray()
    gdal.Unlink(mmapName)
    return(imageArray)


def downloadRadars(numRadars):
    radars = []
    radarInfo = fetchRadarInfo()
    for (key, timeStamp, link) in parseRadarInfo(radarInfo, numRadars):
        data = requests.get(link).content
        saveToFile(str(timeStamp).replace(':', '-').replace(' ', '-'), data)
        image = BytesIO(data)
        iArr = getImageArray(image)
        radar = {
            'key': key,
            'timeStamp': timeStamp,
            'iArr': iArr,
            'image': image,
            'downloadedAt': datetime.utcnow()
        }
        radars.append(radar)
    return(radars)


if __name__ == '__main__':
    radars = downloadRadars(10)
    print(radars)

import db

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
from pymongo import ASCENDING

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


def parseRadarInfo(radarInfo):
    maxEntries = 10
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


def getImageArray(image):
    mmapName = '/vsimem/' + str(uuid4())
    gdal.FileFromMemBuffer(mmapName, image.read())
    dataset = gdal.Open(mmapName)
    imageArray = dataset.GetRasterBand(1).ReadAsArray()
    gdal.Unlink(mmapName)
    return(imageArray)


def identifyRainMasses(arr):
    arr = (arr != 0) & (arr != 255)
    rainMasses = measure.label(arr, background=0, neighbors=8,)
    rainMasses[rainMasses == 0] = 255
    return(rainMasses)


def processRadars(radarInfo):
    dbRadars = db.getDBRadarCollection()

    for (key, timeStamp, link) in parseRadarInfo(radarInfo):
        # check if radar is already in db
        if (dbRadars.count_documents({'key': key}, limit=1) == 0):
            # fetch image and store itlink = 'https://opendata-download-radar.smhi.se/api/version/latest/area/sweden/product/comp/latest.tif'
            image = BytesIO(requests.get(link).content)
            iArr = getImageArray(image)
            rainMasses = identifyRainMasses(iArr)
            post = {
                'key': key,
                'timeStamp': timeStamp,
                'rainMasses': pickle.dumps(rainMasses, protocol=2),
                'createdAt': datetime.utcnow()
            }
            dbRadars.insert_one(post)
            dbRadars.create_index(
                [('timeStamp', ASCENDING)], unique=True)
            plt.figure(figsize=(10, 15))
            plt.imshow(rainMasses)


radarInfo = fetchRadarInfo()
processRadars(radarInfo)

import db
from RainField import RainField
import pymongo
from RainFieldGraph import RainFieldGraph


def getRainFieldsFromDB(limit=10):
    rainFields = []
    dbRadars = db.getDBRadarCollection()
    for radar in dbRadars.find().sort('timeStamp', pymongo.DESCENDING).limit(limit):
        rainField = RainField(
            radar['key'],
            radar['timeStamp'],
            radar['rainMasses'],
            radar['createdAt']
        )
        rainFields.append(rainField)
    return(rainFields)


def makeConnection(rf1, rf2, graph):
    if (not graph.connectionExists(rf1)):
        pass


rainFields = getRainFieldsFromDB()
# latest first
print(*[''.join([str(rf.timeStamp), '\n']) for rf in rainFields])


graph = RainFieldGraph()
for i in range(len(rainFields) - 1):
    makeConnection(rainFields[i], rainFields[i + 1], graph)

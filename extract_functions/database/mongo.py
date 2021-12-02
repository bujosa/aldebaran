import pymongo
from datetime import datetime
import os

#Vehicle data manager class
class VehicleDataManager():
    def __init__(self): 
            self.connection = pymongo.MongoClient(os.environ['MONGO_DB_URI'])
            db = self.connection[os.environ['MONGO_DB_NAME']]
            self.collection = db[datetime.today().strftime('%Y-%m-%d')]

    def addCar(self, vehicleObject):
        self.collection.insert_one(vehicleObject)

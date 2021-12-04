import pymongo
from datetime import datetime
import os

#Vehicle data manager class
class VehicleDataManagerDom():
    def __init__(self): 
            self.connection = pymongo.MongoClient(os.environ['MONGO_DB_URI'])
            db = self.connection['MELI_RD_V3']
            collection_name=datetime.today().strftime('%Y-%m-%d')
            self.collection = db[collection_name]

    def addCar(self, vehicleObject):
        self.collection.insert_one(vehicleObject)

from pymongo import MongoClient
import os
mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(mongo_uri)
db = client["mydb"]
users_collection=db["Users"]
from pymongo import MongoClient
import os
client = MongoClient("mongodb://localhost:27017/")
db = client["mydb"]

if "Users" not in db.list_collection_names():
    db.create_collection("Users")
    print("Users collection created.")
else:
    print("Users collection already exists.")
    
users_collection=db["Users"]
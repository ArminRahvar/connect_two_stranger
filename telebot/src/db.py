import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client.stranger_telebot
col = db.users

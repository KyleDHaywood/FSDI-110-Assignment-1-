import pymongo
import certifi

mongo_url = 'mongodb+srv://FSDI:classtest@cluster0.2hlja.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'

client = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())

db = client.get_database("HobbyStore")
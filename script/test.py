from pprint import pprint
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["kimo"]
courses = db["courses"]
chapters = db["chapters"]

res = courses.aggregate([{
    "$graphLookup": {
        "from": "chapters",
        "startWith": "$chapters",
        "connectFromField": "chapters",
        "connectToField": "_id",
        "as": "chapters"
    }
}])

for course in res:
    pprint(course)
import json
import pymongo
import datetime
# from bson.dbref import DBRef

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Drop database if it exists
client.drop_database("kimo")

# Create a database
db = client["kimo"]

# Create a collection for courses
courses_collection = db["courses"]
courses_collection.create_index([('name', 1)])  # Index for sorting by course title
courses_collection.create_index([('date', -1)])  # Index for sorting by date
courses_collection.create_index([('domain', 1)])  # Index for sorting by date

# Create a collection for chapters
chapters_collection = db["chapters"]
courses_collection.create_index([('course_id', 1)])  # Index for sorting by date

# Create a collection for ratings
ratings_collection = db["ratings"]
courses_collection.create_index([('chapter_id', 1)])  # Index for sorting by date

# Parse course information from courses.json
with open('./script/courses.json', 'r') as f:
    parsed_data = json.load(f)

for i, course in parsed_data.items():
    course_doc = {
        "_id": i, # Not required but useful for testing
        "name": course['name'],
        "date":datetime.datetime.fromtimestamp(course['date']),
        "description":course['description'],
        "domain":course['domain'],
        "chapters":[],
        # "rating": 0.5 # Start halfway
    }
    for chapter in course['chapters']:
        chapter_doc = {
                "name":chapter['name'],
                "text":chapter['text'],
                "rating": None # Start halfway
            }
        insert_res = chapters_collection.insert_one(chapter_doc)
        course_doc['chapters'].append(insert_res.inserted_id)
        # course_doc['chapters'].append(DBRef("chapters", insert_res.inserted_id))
    insert_res = courses_collection.insert_one(course_doc)
    # Store course_id in chapter for easy access
    chapters_collection.update_many(
        {'_id': { "$in" : course_doc['chapters']}}, 
        {"$set": {"course_id":insert_res.inserted_id}}
        )
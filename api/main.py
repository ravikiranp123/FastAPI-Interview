import os
import uvicorn
from fastapi import Body, FastAPI
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()
# client = MongoClient('mongodb://localhost:27017/')
client = MongoClient(f'mongodb://{os.getenv("MONGO_HOST")}:27017/')
db = client['kimo']
courses_collection = db['courses']
chapters_collection = db['chapters']
ratings_collection = db['ratings']

@app.get('/courses')
def get_courses(sort: str = 'name', domain: str = None):
    # Filter courses by domain if provided
    filter_query = {} if domain is None else {'domain': { "$in" : domain.split(",")}}

    # Determine the sorting order
    sort_order = 1  # Ascending order, for sort = name
    if sort == 'date':
        sort_order = -1  # Descending order
    elif sort == 'rating':
        sort_order = -1  # Descending order

    courses = courses_collection.aggregate([
        {"$match": filter_query}, 
        {"$sort": {sort:sort_order}}, 
        {
            "$graphLookup": {
                "from": "chapters",
                "startWith": "$chapters",
                "connectFromField": "chapters",
                "connectToField": "_id",
                "as": "chapters"
            }
    }])
    courses_list = []
    for course in courses:
        course['_id'] = str(course['_id'])
        courses_list.append(course)
        for chapter in course["chapters"]:
            chapter['_id'] = str(chapter['_id'])
            chapter['course_id'] = str(chapter['course_id'])

    return courses_list

@app.get('/courses/{course_id}')
def get_course(course_id: str):
    courses = courses_collection.aggregate([
        {"$match": {'_id': ObjectId(course_id)}}, 
        {
            "$graphLookup": {
                "from": "chapters",
                "startWith": "$chapters",
                "connectFromField": "chapters",
                "connectToField": "_id",
                "as": "chapters"
            }
    }])
    courses_list = []
    for course in courses:
        course['_id'] = str(course['_id'])
        courses_list.append(course)
        for chapter in course["chapters"]:
            chapter['_id'] = str(chapter['_id'])
            chapter['course_id'] = str(chapter['course_id'])
    return courses_list[0]

@app.get('/courses/{course_id}/chapters/{chapter_id}/')
def get_chapter(course_id: str, chapter_id: str):
    chapter = chapters_collection.find_one({'_id': ObjectId(chapter_id), 'course_id': ObjectId(course_id)})
    if not chapter:
        return {"message":"Chapter not found"}
    chapter['_id'] = str(chapter['_id'])
    chapter['course_id'] = str(chapter['course_id'])
    return chapter

@app.post('/courses/{course_id}/chapters/{chapter_id}/rate')
def rate_chapter(course_id: str, chapter_id: str, body = Body()):
    rating = body['rating']
    user_id = body['user_id']
    
    if rating not in (0,1):
        return {"message": "Invalid Rating"}
    
    ratings_collection.insert_one({'chapter_id': ObjectId(chapter_id), 'user_id': user_id, 'rating': rating})
    
    # Please note, ideally this is run as a trigger every time a document is inserted into ratings collection
    # For now, we shall update them here. 
    # Also, we need to validate if the chapter is part of the course. For now, we shall assume it always is
    
    updated_chapter_rating = ratings_collection.aggregate([
        {
            "$match": {"chapter_id": {"$eq": ObjectId(chapter_id)}, "rating":{"$ne":"null"}}
        },
        {
            "$group":{
                "_id":"$chapter_id",
                "rating":{"$avg": "$rating"}
            }
        }
    ])
    updated_chapter_rating = list(updated_chapter_rating)[0]['rating']
    chapters_collection.update_one({'_id': ObjectId(chapter_id)}, {'$set': {'rating': updated_chapter_rating}})
    
    updated_course_rating = chapters_collection.aggregate([
        {
            "$match": {"course_id": {"$eq": ObjectId(course_id)}, "rating":{"$ne":"null"}}
        },
        {
            "$group":{
                "_id":"$course_id",
                "rating":{"$avg": "$rating"}
            }
        }
    ])
    updated_course_rating = list(updated_course_rating)[0]['rating']
    courses_collection.update_one({'_id': ObjectId(course_id)}, {'$set': {'rating': updated_course_rating}})
    
    return {'message': 'Chapter rating updated.'}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
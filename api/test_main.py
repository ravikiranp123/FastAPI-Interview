from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_courses():
    responses = client.get('/courses')
    assert responses.status_code == 200
    assert responses.json() is not None
    assert len(responses.json()) == 4
    
    # Sort be date descending
    responses = client.get('/courses?sort=date').json()
    assert responses[0]['date'] == "2022-08-08T02:30:00"
    assert responses[1]['date'] == "2022-05-26T02:30:00"
    assert responses[2]['date'] == "2018-06-28T02:30:00"
    assert responses[3]['date'] == "2017-08-11T02:30:00"
    
    # Check for domain
    responses = client.get('/courses?domain=artificial intelligence').json()
    for response in responses:
        assert 'artificial intelligence' in response['domain']

def test_get_course():
    response = client.get('/courses/648f28dae4f88ba31472eb14')
    assert response.status_code == 200
    assert response.json() is not None
    assert response.json()['name'] == "Computer Vision Course"

def test_get_chapter():
    response = client.get('/courses/648f28dae4f88ba31472eb14/chapters/648f28dae4f88ba31472eb13')
    assert response.status_code == 200
    assert response.json() is not None
    assert response.json()["name"] == "Adversarial Examples and Adversarial Training"

def test_rate_chapter():
    course = client.get('/courses/648f28dae4f88ba31472eb14').json()
    initial_course_rating = course['rating']
    chapter = client.get('/courses/648f28dae4f88ba31472eb14/chapters/648f28dae4f88ba31472eb05').json()
    initial_chapter_rating = chapter['rating']
    response = client.post('/courses/648f28dae4f88ba31472eb14/chapters/648f28dae4f88ba31472eb05/rate', 
    headers={
        "Accept": "*/*",
        "Content-Type": "application/json" 
    },
    json={
        "rating": 0,
        "user_id":"1"
    }).json()
    
    assert response['message'] == "Chapter rating updated."
    
    course = client.get('/courses/648f28dae4f88ba31472eb14').json()
    final_course_rating = course['rating']
    chapter = client.get('/courses/648f28dae4f88ba31472eb14/chapters/648f28dae4f88ba31472eb05').json()
    final_chapter_rating = chapter['rating']
    
    assert initial_course_rating > final_course_rating
    assert initial_chapter_rating > final_chapter_rating
    
    initial_course_rating = final_course_rating
    initial_chapter_rating = final_chapter_rating
    
    response = client.post('/courses/648f28dae4f88ba31472eb14/chapters/648f28dae4f88ba31472eb05/rate', 
    headers={
        "Accept": "*/*",
        "Content-Type": "application/json" 
    },
    json={
        "rating": 1,
        "user_id":"1"
    }).json()
    
    assert response['message'] == "Chapter rating updated."
    
    course = client.get('/courses/648f28dae4f88ba31472eb14').json()
    final_course_rating = course['rating']
    chapter = client.get('/courses/648f28dae4f88ba31472eb14/chapters/648f28dae4f88ba31472eb05').json()
    final_chapter_rating = chapter['rating']
    
    assert initial_course_rating < final_course_rating
    assert initial_chapter_rating < final_chapter_rating
    

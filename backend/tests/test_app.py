import pytest
from flask import json
from app import app, db, User, Event

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/event_backend_test'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  
        yield client
        db.drop_all()  

def test_leave_event(client):
    # Step 1: Organizer registers and logs in.
    client.post('/register', json={'name': 'Organizer01', 'role': 'Organizer', 'password': 'password123'})
    client.post('/login', json={'name': 'Organizer01', 'password': 'password123'})

    # step 2: Organizer Creates an event. 
    event_response = client.post('/add_event', json={
        'event_title': 'Event',
        'event_location': 'Location',
        'event_date': '2024-01-03T00:00:00',
        'event_duration': '01:00:00',
        'organizer_id': 1
    })
    assert 'event_id' in event_response.get_json()
    event_id = event_response.get_json()['event_id']

    # Step 3: Organizer logs out.
    logout_response = client.post('/logout')
    assert logout_response.status_code == 200

    # Step 4: Joiner registers and logs in.
    client.post('/register', json={'name': 'Joiner01', 'role': 'Joiner', 'password': 'password123'})
    client.post('/login', json={'name': 'Joiner01', 'password': 'password123'})

    # Step 5: Joiner joins the event created by the organizer in step 2.
    client.post(f'/join_event/{event_id}')
    check_response = client.get(f'/check_join_status/{event_id}')
    assert check_response.status_code == 200
    assert check_response.get_json()['joined'] is True
    
    # Step 6: Joiner leaves the event that they joined in step 5
    leave_response = client.post(f'/leave_event/{event_id}')
    assert leave_response.status_code == 200
    assert 'message' in leave_response.get_json()
    check_response = client.get(f'/check_join_status/{event_id}')
    assert check_response.get_json()['joined'] is False
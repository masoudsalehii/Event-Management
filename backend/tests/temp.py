def test_check_join_status(client):
    client.post('/register', json={'name': 'Organizer5', 'role': 'Organizer', 'password': 'password123'})
    client.post('/login', json={'name': 'Organizer5', 'password': 'password123'})
    # Create and join an event
    event_response = client.post('/add_event', json={
        'event_title': 'Event3',
        'event_location': 'Location3',
        'event_date': '2024-01-03T00:00:00',
        'event_duration': '01:00:00',
        'organizer_id': 1
    })
    assert 'event_id' in event_response.get_json()
    event_id = event_response.get_json()['event_id']
    logout_response = client.post('/logout')
    assert logout_response.status_code == 200

    client.post('/register', json={'name': 'Joiner4', 'role': 'Joiner', 'password': 'password123'})
    client.post('/login', json={'name': 'Joiner4', 'password': 'password123'})
    client.post(f'/join_event/{event_id}')
    check_response = client.get(f'/check_join_status/{event_id}')
    assert check_response.status_code == 200
    assert check_response.get_json()['joined'] is True
    


def test_leave_event(client):
    client.post('/register', json={'name': 'Organizer6', 'role': 'Organizer', 'password': 'password123'})
    client.post('/login', json={'name': 'Organizer6', 'password': 'password123'})
    # Create and join an event
    event_response = client.post('/add_event', json={
        'event_title': 'Event4',
        'event_location': 'Location3',
        'event_date': '2024-01-03T00:00:00',
        'event_duration': '01:00:00',
        'organizer_id': 1
    })
    assert 'event_id' in event_response.get_json()
    event_id = event_response.get_json()['event_id']
    logout_response = client.post('/logout')
    assert logout_response.status_code == 200

    client.post('/register', json={'name': 'Joiner5', 'role': 'Joiner', 'password': 'password123'})
    client.post('/login', json={'name': 'Joiner5', 'password': 'password123'})
    client.post(f'/join_event/{event_id}')
    check_response = client.get(f'/check_join_status/{event_id}')
    assert check_response.status_code == 200
    assert check_response.get_json()['joined'] is True
    
    leave_response = client.post(f'/leave_event/{event_id}')
    assert leave_response.status_code == 200
    assert 'message' in leave_response.get_json()
    check_response = client.get(f'/check_join_status/{event_id}')
    assert check_response.get_json()['joined'] is False

    
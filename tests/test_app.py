import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_redirect_root():
    response = client.get("/", follow_redirects=False)  # Don't follow redirects
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    assert response.json() == activities
    assert "Chess Club" in response.json()

def test_signup_success():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]

def test_signup_already_registered():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # This email is already registered
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_invalid_activity():
    activity_name = "NonExistentClub"
    email = "student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

@pytest.fixture(autouse=True)
def cleanup():
    # Store original activities state
    original_activities = activities.copy()
    yield
    # Restore original activities state after each test
    activities.clear()
    activities.update(original_activities)
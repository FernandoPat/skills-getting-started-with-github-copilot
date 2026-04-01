from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

original_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: ensure fresh in-memory state per test
    activities.clear()
    activities.update(deepcopy(original_activities))
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert isinstance(payload["Chess Club"], dict)


def test_signup_for_activity_success_and_duplicate():
    # Arrange
    email = "newstudent@mergington.edu"
    url = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}

    # Act - duplicate signup
    response_duplicate = client.post(url, params={"email": email})

    # Assert duplicate rejection
    assert response_duplicate.status_code == 400
    assert response_duplicate.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_nonexistent_activity():
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.post("/activities/Unknown/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success_and_missing():
    # Arrange
    email = "michael@mergington.edu"
    url = "/activities/Chess%20Club/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}

    # Act - removing again should be not found
    response_not_found = client.delete(url, params={"email": email})

    # Assert
    assert response_not_found.status_code == 404
    assert response_not_found.json()["detail"] == "Participant not found in this activity"


def test_remove_participant_from_nonexistent_activity():
    # Arrange
    email = "nobody@mergington.edu"

    # Act
    response = client.delete("/activities/Unknown/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_root_redirects_to_static_index():
    # Arrange

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

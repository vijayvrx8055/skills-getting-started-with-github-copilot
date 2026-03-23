import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a FastAPI TestClient for making requests to the app."""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Provide sample activity data for tests."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Test Activity": {
            "description": "Activity for testing",
            "schedule": "Every day",
            "max_participants": 2,
            "participants": []
        }
    }


@pytest.fixture
def reset_activities(sample_activities, monkeypatch):
    """Reset activities to sample data before each test."""
    monkeypatch.setattr("src.app.activities", sample_activities)
    return sample_activities

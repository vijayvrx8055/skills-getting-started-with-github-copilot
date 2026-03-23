import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that GET /activities returns a 200 status code."""
        # Arrange
        # (fixture provides client and sample activities)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        # Arrange
        # (fixture provides client and sample activities)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert len(data) == 4
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Test Activity" in data

    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test that each activity has the correct data structure."""
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity in data.items():
            assert expected_keys.issubset(activity.keys())
            assert isinstance(activity["participants"], list)

    def test_get_activities_participants_populated(self, client, reset_activities):
        """Test that participants list contains expected data."""
        # Arrange
        expected_chess_participants = {"michael@mergington.edu", "daniel@mergington.edu"}

        # Act
        response = client.get("/activities")
        data = response.json()
        actual_participants = set(data["Chess Club"]["participants"])

        # Assert
        assert actual_participants == expected_chess_participants

    def test_get_activities_empty_participants_allowed(self, client, reset_activities):
        """Test that activities can have empty participants list."""
        # Arrange
        # (fixture provides an empty Test Activity)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert len(data["Test Activity"]["participants"]) == 0


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup to an activity."""
        # Arrange
        activity_name = "Test Activity"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "successfully signed up" in response.json()["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity."""
        # Arrange
        activity_name = "Test Activity"
        email = "newstudent@mergington.edu"

        # Act
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert email in data["Test Activity"]["participants"]

    def test_signup_duplicate_rejected(self, client, reset_activities):
        """Test that duplicate signup is rejected with 400 error."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_rejected(self, client, reset_activities):
        """Test that signup to non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_full_activity_rejected(self, client, reset_activities):
        """Test that signup to full activity is rejected with 400 error."""
        # Arrange
        activity_name = "Test Activity"
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        student3 = "student3@mergington.edu"
        # Test Activity has max 2 participants, currently empty

        # Act: Fill the activity to capacity
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={student1}"
        )
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={student2}"
        )

        # Act: Try to add a third (should fail)
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={student3}"
        )

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"]

    def test_signup_response_format(self, client, reset_activities):
        """Test that signup response has correct format."""
        # Arrange
        activity_name = "Test Activity"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_participant_count_increases(self, client, reset_activities):
        """Test that participant count increases after successful signup."""
        # Arrange
        activity_name = "Chess Club"
        email = "newcomer@mergington.edu"

        # Act: Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity_name]["participants"])

        # Act: Add new participant
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )

        # Act: Get new count
        response2 = client.get("/activities")
        new_count = len(response2.json()[activity_name]["participants"])

        # Assert
        assert new_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "successfully unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert email not in data[activity_name]["participants"]

    def test_unregister_nonexistent_participant_rejected(self, client, reset_activities):
        """Test that unregistering non-existent participant returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_rejected(self, client, reset_activities):
        """Test that unregister from non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_participant_count_decreases(self, client, reset_activities):
        """Test that participant count decreases after successful unregister."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act: Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity_name]["participants"])

        # Act: Remove a participant
        client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )

        # Act: Get new count
        response2 = client.get("/activities")
        new_count = len(response2.json()[activity_name]["participants"])

        # Assert
        assert new_count == initial_count - 1

    def test_unregister_frees_up_capacity(self, client, reset_activities):
        """Test that unregistering frees up capacity in full activity."""
        # Arrange
        activity_name = "Test Activity"
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        student3 = "student3@mergington.edu"
        # Test Activity has max 2 participants

        # Act: Fill the activity to capacity
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={student1}"
        )
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={student2}"
        )

        # Act: Verify it's full (attempt 3rd signup should fail)
        verify_full = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={student3}"
        )
        assert verify_full.status_code == 400

        # Act: Remove one participant to free up capacity
        client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={student1}"
        )

        # Act: Try to add again (should now succeed)
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={student3}"
        )

        # Assert
        assert response.status_code == 200

    def test_unregister_response_format(self, client, reset_activities):
        """Test that unregister response has correct format."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)
        assert email in data["message"]
        assert activity_name in data["message"]

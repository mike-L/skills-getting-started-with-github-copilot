"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture
def client():
    """Test client fixture for FastAPI app"""
    return TestClient(app)


class TestActivitiesAPI:
    """Test suite for activities API endpoints"""

    def test_get_activities(self, client):
        """Test GET /activities returns all activities with correct structure"""
        # Arrange - no setup needed for GET request

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0  # Should have activities

        # Check structure of first activity
        first_activity = next(iter(data.values()))
        required_keys = ["description", "schedule", "max_participants", "participants"]
        for key in required_keys:
            assert key in first_activity
        assert isinstance(first_activity["participants"], list)

    def test_signup_successful(self, client):
        """Test POST /activities/{name}/signup successfully registers a student"""
        # Arrange
        activity_name = "Chess Club"
        email = "test_signup@example.com"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert f"Signed up {email} for {activity_name}" == result["message"]

        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity_name]["participants"]

    def test_signup_duplicate_prevention(self, client):
        """Test POST /activities/{name}/signup prevents duplicate signups"""
        # Arrange
        activity_name = "Programming Class"
        email = "test_duplicate@example.com"

        # Act - First signup (should succeed)
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response1.status_code == 200

        # Act - Second signup (should fail)
        response2 = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response2.status_code == 400
        result = response2.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]

    def test_signup_invalid_activity(self, client):
        """Test POST /activities/{name}/signup fails for non-existent activity"""
        # Arrange
        invalid_activity = "NonExistent Club"
        email = "test_invalid@example.com"

        # Act
        response = client.post(f"/activities/{invalid_activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" == result["detail"]

    def test_unregister_successful(self, client):
        """Test DELETE /activities/{name}/signup successfully unregisters a student"""
        # Arrange
        activity_name = "Gym Class"
        email = "test_unregister@example.com"

        # First, sign up the student
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert f"Unregistered {email} from {activity_name}" == result["message"]

        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity_name]["participants"]

    def test_unregister_not_signed_up(self, client):
        """Test DELETE /activities/{name}/signup fails for student not signed up"""
        # Arrange
        activity_name = "Debate Team"
        email = "test_not_signed@example.com"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Student not signed up for this activity" == result["detail"]

    def test_unregister_invalid_activity(self, client):
        """Test DELETE /activities/{name}/signup fails for non-existent activity"""
        # Arrange
        invalid_activity = "Invalid Club"
        email = "test_invalid_delete@example.com"

        # Act
        response = client.delete(f"/activities/{invalid_activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" == result["detail"]

    def test_root_redirect(self, client):
        """Test GET / serves the static frontend"""
        # Arrange - no setup needed

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        assert "Mergington High School" in response.text
        assert "<!DOCTYPE html>" in response.text
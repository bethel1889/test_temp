import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.entities.room_entity import Room as RoomEntity

# The service functions are mocked to isolate the controller and test its behavior.
# This prevents actual calls to the LiveKit API during E2E tests of the controller.
@patch('src.features.rooms.service.create_room_in_livekit', new_callable=AsyncMock)
def test_create_room_endpoint_success(mock_create_livekit, client: TestClient, db_session: Session):
    """
    Test the POST /v1/rooms endpoint for successful room creation.
    """
    # Arrange
    # Mock the response from the LiveKit service function
    mock_livekit_room = MagicMock()
    mock_livekit_room.sid = "RM_test_sid_e2e"
    mock_create_livekit.return_value = mock_livekit_room
    
    room_data = {
        "name": "e2e-test-room",
        "access_type": "public",
        "empty_timeout": 300,
        "max_participants": 10
    }

    # Act
    response = client.post("/v1/rooms/", json=room_data)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == room_data["name"]
    assert data["access_type"] == room_data["access_type"]
    assert "id" in data
    assert "created_at" in data
    assert data["livekit_sid"] == "RM_test_sid_e2e"

    # Verify that the data was saved to the test database
    db_room = db_session.query(RoomEntity).filter(RoomEntity.name == room_data["name"]).first()
    assert db_room is not None
    assert db_room.name == room_data["name"]

def test_create_room_endpoint_already_exists(client: TestClient, db_session: Session):
    """
    Test the POST /v1/rooms endpoint when a room with the same name already exists.
    """
    # Arrange: First, create a room in the database.
    existing_room = RoomEntity(
        name="existing-room-e2e", 
        livekit_sid="RM_dummy_sid",
        access_type="public"
    )
    db_session.add(existing_room)
    db_session.commit()

    room_data = {"name": "existing-room-e2e", "access_type": "public"}

    # Act
    response = client.post("/v1/rooms/", json=room_data)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room 'existing-room-e2e' already exists."

def test_create_room_endpoint_invalid_input(client: TestClient):
    """
    Test the POST /v1/rooms endpoint with invalid input data.
    FastAPI and Pydantic should handle this automatically.
    """
    # Arrange: Invalid room name with spaces
    invalid_data = {
        "name": "invalid room name",
        "access_type": "public"
    }
    
    # Act
    response = client.post("/v1/rooms/", json=invalid_data)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["msg"] is not None # Check that there is a validation error message

def test_create_join_token_endpoint_success(client: TestClient, db_session: Session):
    """
    Test the POST /v1/rooms/{room_name}/token endpoint for successful token generation.
    """
    # Arrange: Create a room to generate a token for.
    room = RoomEntity(name="token-room", livekit_sid="RM_dummy", access_type="public")
    db_session.add(room)
    db_session.commit()
    
    token_request_data = {
        "identity": "test-user-e2e",
        "name": "Test User"
    }

    # Act
    response = client.post("/v1/rooms/token-room/token", json=token_request_data)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "token" in data
    assert isinstance(data["token"], str)

def test_create_join_token_endpoint_room_not_found(client: TestClient):
    """
    Test the token generation endpoint for a room that does not exist.
    """
    # Arrange
    token_request_data = {
        "identity": "test-user-e2e",
        "name": "Test User"
    }

    # Act
    response = client.post("/v1/rooms/non-existent-room/token", json=token_request_data)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room 'non-existent-room' not found."
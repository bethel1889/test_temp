import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from sqlalchemy.orm import Session
from livekit import api

from src.features.rooms import service as room_service
from src.features.rooms import models as room_models
from src.entities.room_entity import Room as RoomEntity
from src.exceptions import RoomAlreadyExistsException, RoomNotFoundException, LiveKitServiceException

@pytest.mark.asyncio
@patch('src.features.rooms.service.create_room_in_livekit', new_callable=AsyncMock)
@patch('src.features.rooms.service.create_room_in_db')
@patch('src.features.rooms.service.get_room_by_name')
async def test_create_room_service_success(
    mock_get_room,
    mock_create_db,
    mock_create_livekit,
    db_session: Session
):
    """
    Test successful creation of a room in the service layer.
    Ensures that LiveKit and DB creation functions are called correctly.
    """
    # Arrange
    mock_get_room.return_value = None
    
    mock_livekit_room = MagicMock(spec=api.Room)
    mock_livekit_room.sid = "RM_test_sid"
    mock_create_livekit.return_value = mock_livekit_room

    mock_db_room = RoomEntity(id=1, name="test-room", livekit_sid="RM_test_sid")
    mock_create_db.return_value = mock_db_room

    request = room_models.RoomCreateRequest(
        name="test-room",
        access_type="public",
        empty_timeout=600,
        max_participants=50
    )

    # Act
    result = await room_service.create_room_service(db_session, request)

    # Assert
    mock_get_room.assert_called_once_with(db_session, "test-room")
    mock_create_livekit.assert_awaited_once_with(
        name="test-room",
        empty_timeout=600,
        max_participants=50
    )
    mock_create_db.assert_called_once_with(db_session, request, "RM_test_sid")
    assert result == mock_db_room

@pytest.mark.asyncio
@patch('src.features.rooms.service.get_room_by_name')
async def test_create_room_service_already_exists(mock_get_room, db_session: Session):
    """
    Test that creating a room with a name that already exists raises RoomAlreadyExistsException.
    """
    # Arrange
    mock_get_room.return_value = RoomEntity(id=1, name="existing-room")
    request = room_models.RoomCreateRequest(name="existing-room", access_type="public")

    # Act & Assert
    with pytest.raises(RoomAlreadyExistsException):
        await room_service.create_room_service(db_session, request)
    mock_get_room.assert_called_once_with(db_session, "existing-room")

@pytest.mark.asyncio
@patch('src.features.rooms.service.create_room_in_livekit', new_callable=AsyncMock)
@patch('src.features.rooms.service.get_room_by_name')
async def test_create_room_service_livekit_fails(mock_get_room, mock_create_livekit, db_session: Session):
    """
    Test that if the LiveKit API call fails, LiveKitServiceException is raised.
    """
    # Arrange
    mock_get_room.return_value = None
    mock_create_livekit.side_effect = LiveKitServiceException(detail="API error")
    request = room_models.RoomCreateRequest(name="new-room", access_type="public")

    # Act & Assert
    with pytest.raises(LiveKitServiceException):
        await room_service.create_room_service(db_session, request)
    mock_create_livekit.assert_awaited_once()

def test_create_join_token_service_success(db_session: Session):
    """
    Test successful creation of a join token when the room exists.
    """
    # Arrange
    room = RoomEntity(id=1, name="test-room", livekit_sid="RM_test")
    db_session.add(room)
    db_session.commit()

    request = room_models.JoinTokenRequest(identity="user123", name="Alice")

    # Act
    token = room_service.create_join_token_service(db_session, "test-room", request)

    # Assert
    assert isinstance(token, str)
    assert len(token) > 20  # JWTs are long strings

def test_create_join_token_service_room_not_found(db_session: Session):
    """
    Test that creating a join token for a non-existent room raises RoomNotFoundException.
    """
    # Arrange
    request = room_models.JoinTokenRequest(identity="user123", name="Alice")

    # Act & Assert
    with pytest.raises(RoomNotFoundException):
        room_service.create_join_token_service(db_session, "non-existent-room", request)
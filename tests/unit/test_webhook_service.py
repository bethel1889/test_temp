import pytest
from unittest.mock import patch, MagicMock
from livekit import api

from src.features.webhooks import service as webhook_service

@patch('src.features.webhooks.service.webhook_receiver')
def test_process_webhook_event_success(mock_receiver):
    """
    Test that a valid webhook body and authorization header are correctly processed.
    """
    # Arrange
    mock_event = MagicMock(spec=api.WebhookEvent)
    mock_event.event = "test_event"
    mock_receiver.receive.return_value = mock_event
    
    body = '{"event": "test_event"}'
    auth_header = "Bearer valid_token"
    
    # Act
    result = webhook_service.process_webhook_event(body, auth_header)
    
    # Assert
    mock_receiver.receive.assert_called_once_with(body, auth_header)
    assert result == mock_event

@patch('src.features.webhooks.service.webhook_receiver')
def test_process_webhook_event_validation_failure(mock_receiver):
    """
    Test that if the webhook receiver fails validation, it raises an exception.
    """
    # Arrange
    mock_receiver.receive.side_effect = Exception("Invalid signature")
    body = '{"event": "test_event"}'
    auth_header = "Bearer invalid_token"
    
    # Act & Assert
    with pytest.raises(Exception, match="Invalid signature"):
        webhook_service.process_webhook_event(body, auth_header)
    
    mock_receiver.receive.assert_called_once_with(body, auth_header)

@patch('src.features.webhooks.service.logger')
def test_handle_event_logic(mock_logger):
    """
    Test the routing logic within handle_event_logic for different event types.
    """
    # --- Test participant_joined event ---
    participant_joined_event = MagicMock(spec=api.WebhookEvent)
    participant_joined_event.event = "participant_joined"
    participant_joined_event.participant.identity = "user1"
    participant_joined_event.participant.name = "Alice"
    participant_joined_event.room.name = "test-room"
    participant_joined_event.room.sid = "RM_sid"
    
    webhook_service.handle_event_logic(participant_joined_event)
    mock_logger.info.assert_any_call("Received webhook event: participant_joined")
    mock_logger.info.assert_any_call(
        "Participant 'user1' (Alice) joined room 'test-room' (SID: RM_sid)."
    )

    # --- Test room_finished event ---
    room_finished_event = MagicMock(spec=api.WebhookEvent)
    room_finished_event.event = "room_finished"
    room_finished_event.room.name = "test-room"
    room_finished_event.room.sid = "RM_sid"
    room_finished_event.room.duration = 120
    
    webhook_service.handle_event_logic(room_finished_event)
    mock_logger.info.assert_any_call("Received webhook event: room_finished")
    mock_logger.info.assert_any_call(
        "Room 'test-room' (SID: RM_sid) has finished. Duration: 120s."
    )

    # --- Test unhandled event ---
    unhandled_event = MagicMock(spec=api.WebhookEvent)
    unhandled_event.event = "unhandled_event_type"
    
    webhook_service.handle_event_logic(unhandled_event)
    mock_logger.info.assert_any_call("Received webhook event: unhandled_event_type")
    mock_logger.warning.assert_called_once_with(
        "Received an unhandled webhook event type: unhandled_event_type"
    )
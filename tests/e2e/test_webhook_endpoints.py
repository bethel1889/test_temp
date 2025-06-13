import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient

from src.features.webhooks.models import WebhookConfirmation

# Mock the entire service module to prevent actual processing logic during E2E tests
@patch('src.features.webhooks.controller.webhook_service')
def test_handle_webhook_endpoint_success(mock_service, client: TestClient):
    """
    Test the POST /v1/livekit/webhook endpoint for a successful, valid request.
    """
    # Arrange
    mock_service.process_webhook_event.return_value = MagicMock()
    
    webhook_body = '{"event": "test_event"}'
    headers = {"Authorization": "Bearer valid-jwt"}
    
    # Act
    response = client.post("/v1/livekit/webhook", content=webhook_body, headers=headers)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == WebhookConfirmation().model_dump()
    
    mock_service.process_webhook_event.assert_called_once_with(
        body=webhook_body,
        authorization=headers["Authorization"]
    )
    mock_service.handle_event_logic.assert_called_once()

def test_handle_webhook_endpoint_no_auth_header(client: TestClient):
    """
    Test that the webhook endpoint returns 401 Unauthorized if no Authorization header is provided.
    """
    # Arrange
    webhook_body = '{"event": "test_event"}'
    
    # Act
    response = client.post("/v1/livekit/webhook", content=webhook_body)
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authorization header is required."

@patch('src.features.webhooks.controller.webhook_service')
def test_handle_webhook_endpoint_validation_fails(mock_service, client: TestClient):
    """
    Test that the endpoint returns 400 Bad Request if the service layer raises a validation exception.
    """
    # Arrange
    error_message = "Invalid JWT signature"
    mock_service.process_webhook_event.side_effect = Exception(error_message)
    
    webhook_body = '{"event": "test_event"}'
    headers = {"Authorization": "Bearer invalid-jwt"}
    
    # Act
    response = client.post("/v1/livekit/webhook", content=webhook_body, headers=headers)
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"Webhook validation or processing failed: {error_message}"
    
    mock_service.process_webhook_event.assert_called_once()
    mock_service.handle_event_logic.assert_not_called()
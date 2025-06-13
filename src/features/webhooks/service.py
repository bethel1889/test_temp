# src/features/webhooks/service.py (Corrected)
import logging
from livekit import api
from livekit.api import WebhookEvent

from src.config import settings # <-- Import settings

# Configure a logger for this module
logger = logging.getLogger(__name__)

# --- Webhook Receiver Initialization ---
# Explicitly initialize the TokenVerifier with credentials from our settings.
try:
    token_verifier = api.TokenVerifier(
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET,
    )
except ValueError as e:
    # This provides a clear startup error if credentials are not set.
    raise RuntimeError(f"LiveKit API credentials are not set for TokenVerifier: {e}") from e

# The WebhookReceiver uses the verifier to process incoming events.
webhook_receiver = api.WebhookReceiver(token_verifier)

def process_webhook_event(body: str, authorization: str) -> WebhookEvent:
    """
    Validates and parses a raw webhook request into a structured WebhookEvent.
    """
    event = webhook_receiver.receive(body, authorization)
    return event

def handle_event_logic(event: WebhookEvent):
    """
    Contains the business logic for different types of webhook events.
    """
    logger.info(f"Received webhook event: {event.event}")

    # Example of handling specific events
    if event.event == "participant_joined":
        logger.info(
            f"Participant '{event.participant.identity}' ({event.participant.name}) "
            f"joined room '{event.room.name}' (SID: {event.room.sid})."
        )
    elif event.event == "participant_left":
        logger.info(
            f"Participant '{event.participant.identity}' left room '{event.room.name}'."
        )
    elif event.event == "room_finished":
        logger.info(
            f"Room '{event.room.name}' (SID: {event.room.sid}) has finished. "
            f"Duration: {event.room.duration}s."
        )
    elif event.event == "track_published":
        logger.info(
            f"Track '{event.track.sid}' of type '{event.track.type}' published by "
            f"'{event.participant.identity}' in room '{event.room.name}'."
        )
    else:
        logger.warning(f"Received an unhandled webhook event type: {event.event}")
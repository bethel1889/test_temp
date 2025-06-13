import logging
from fastapi import APIRouter, Request, Header, HTTPException, status
from typing import Optional

from src.features.webhooks import service as webhook_service
from src.features.webhooks import models as webhook_models

# Configure a logger for this module
logger = logging.getLogger(__name__)

# Create an APIRouter for the 'webhooks' feature.
router = APIRouter(
    prefix="/livekit",
    tags=["Webhooks"],
)

@router.post(
    "/webhook",
    response_model=webhook_models.WebhookConfirmation,
    status_code=status.HTTP_200_OK,
    summary="Handle LiveKit Webhooks",
    description=(
        "This endpoint receives, validates, and processes incoming webhooks from a LiveKit server. "
        "It requires a valid 'Authorization' header containing a LiveKit-generated JWT."
    )
)
async def handle_webhook(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Endpoint to process incoming webhooks from LiveKit.

    The 'Authorization' header is crucial for security, as it contains a JWT
    signed by the LiveKit API secret, which this endpoint will verify.

    The raw request body is passed to the service layer for validation and parsing.
    """
    if authorization is None:
        logger.warning("Webhook received without Authorization header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required."
        )

    try:
        # Get the raw body as bytes, then decode to a string
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")

        # The service layer handles validation and parsing
        event = webhook_service.process_webhook_event(
            body=body_str,
            authorization=authorization
        )

        # The service layer contains the business logic for each event type
        webhook_service.handle_event_logic(event)

    except Exception as e:
        # This catches validation errors from `webhook_receiver.receive`
        # (e.g., invalid signature) or any other processing error.
        logger.error(f"Webhook processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook validation or processing failed: {str(e)}"
        )

    return webhook_models.WebhookConfirmation()
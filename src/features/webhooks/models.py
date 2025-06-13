from pydantic import BaseModel, ConfigDict

class WebhookConfirmation(BaseModel):
    """
    Standard success response for a processed webhook.
    """
    status: str = "ok"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok"
            }
        }
    )
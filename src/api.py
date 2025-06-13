from fastapi import APIRouter

from src.features.rooms import controller as rooms_controller
from src.features.webhooks import controller as webhooks_controller

# Create a main API router that will include all the feature-specific routers.
# This acts as the single point of entry for all versioned API routes.
api_router = APIRouter(prefix="/v1")

# Include the router from the 'rooms' feature.
# All routes defined in `rooms_controller` will be prefixed with `/v1`.
api_router.include_router(rooms_controller.router)

# Include the router from the 'webhooks' feature.
# All routes defined in `webhooks_controller` will be prefixed with `/v1`.
api_router.include_router(webhooks_controller.router)


@api_router.get("/health", tags=["Health Check"])
async def health_check():
    """
    A simple health check endpoint to confirm that the API is running.
    """
    return {"status": "ok"}
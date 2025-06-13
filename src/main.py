import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import api_router
from src.features.rooms import service as room_service
from src.database.core import Base, engine

# --- Application Configuration ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create all database tables based on the ORM models.
# This is a simple way to ensure tables exist for development.
# For production, it's highly recommended to use a migration tool like Alembic.
Base.metadata.create_all(bind=engine) # We will use Alembic, so this is commented out.

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Qari Video Conferencing API",
    description="Backend API for the Qari Web3 video conferencing application, powered by LiveKit.",
    version="1.0.0",
)

# --- Middleware Configuration ---
# Configure CORS (Cross-Origin Resource Sharing) to allow requests from the frontend.
# In a production environment, you should restrict the origins to your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for simplicity. Change to specific domain in production.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.).
    allow_headers=["*"],  # Allows all headers.
)

# --- Event Handlers ---
@app.on_event("shutdown")
async def app_shutdown():
    """
    Gracefully close the LiveKit API client when the application shuts down.
    """
    logging.info("Application is shutting down. Closing LiveKit client.")
    await room_service.close_livekit_client()

# --- API Router Inclusion ---
# Include the main router from `api.py`. All API routes will be available under its prefix.
app.include_router(api_router)


# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    """
    A simple root endpoint to confirm the API is accessible.
    """
    return {"message": "Welcome to the Qari API. Visit /docs for documentation."}


# --- Uvicorn Runner (for direct execution) ---
if __name__ == "__main__":
    # This block allows running the app directly with `python src/main.py`
    # Useful for development and debugging.
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Automatically reload on code changes
        log_level="info"
    )
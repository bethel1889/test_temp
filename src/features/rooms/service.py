# src/features/rooms/service.py (Final Corrected Version)
import logging
from sqlalchemy.orm import Session
from livekit import api
# Import DeleteRoomRequest along with the others
from livekit.api import CreateRoomRequest as LiveKitCreateRoomRequest, DeleteRoomRequest

from src.config import settings
from src.features.rooms import models as room_models
from src.entities.room_entity import Room as RoomEntity
from src.exceptions import (
    RoomNotFoundException,
    RoomAlreadyExistsException,
    LiveKitServiceException
)

logger = logging.getLogger(__name__)

# Initialize the LiveKit API client explicitly from our settings object.
try:
    lkapi = api.LiveKitAPI(
        url=settings.LIVEKIT_URL,
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET,
    )
except ValueError as e:
    raise RuntimeError(f"LiveKit API credentials are not configured correctly: {e}") from e

async def create_room_in_livekit(
    name: str,
    empty_timeout: int,
    max_participants: int
) -> api.Room:
    """Calls the LiveKit API to create a new room."""
    try:
        livekit_room = await lkapi.room.create_room(
            LiveKitCreateRoomRequest(
                name=name,
                empty_timeout=empty_timeout,
                max_participants=max_participants,
            )
        )
        return livekit_room
    except Exception as e:
        raise LiveKitServiceException(detail=str(e))

def create_room_in_db(db: Session, request: room_models.RoomCreateRequest, livekit_sid: str) -> RoomEntity:
    """Creates and saves a new room record in the database."""
    db_room = RoomEntity(
        name=request.name,
        livekit_sid=livekit_sid,
        access_type=request.access_type,
        token_address=request.token_address,
        token_amount=request.token_amount,
        nft_address=request.nft_address
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def get_room_by_name(db: Session, name: str) -> RoomEntity | None:
    """Retrieves a room from the database by its name."""
    return db.query(RoomEntity).filter(RoomEntity.name == name).first()

async def create_room_service(db: Session, request: room_models.RoomCreateRequest) -> RoomEntity:
    """Orchestrates the creation of a new room."""
    if get_room_by_name(db, request.name):
        raise RoomAlreadyExistsException(room_name=request.name)

    livekit_room = await create_room_in_livekit(
        name=request.name,
        empty_timeout=request.empty_timeout,
        max_participants=request.max_participants
    )
    db_room = create_room_in_db(db, request, livekit_room.sid)
    return db_room

def create_join_token_service(db: Session, room_name: str, request: room_models.JoinTokenRequest) -> str:
    """Generates a JWT access token for a user to join a specific room."""
    db_room = get_room_by_name(db, room_name)
    if not db_room:
        raise RoomNotFoundException(room_name=room_name)

    token = (
        api.AccessToken(
            api_key=settings.LIVEKIT_API_KEY,
            api_secret=settings.LIVEKIT_API_SECRET,
        )
        .with_identity(request.identity)
        .with_name(request.name)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
    )
    return token.to_jwt()

async def delete_room_service(db: Session, room_name: str):
    """
    Deletes a room from LiveKit and the local database.
    """
    db_room = get_room_by_name(db, room_name)
    if not db_room:
        logger.warning(f"Room '{room_name}' not found in local DB, but attempting LiveKit deletion.")
    
    try:
        logger.info(f"Deleting room '{room_name}' from LiveKit server...")
        # --- THIS IS THE FIX ---
        # We must create a DeleteRoomRequest object and pass that to the method.
        delete_request = DeleteRoomRequest(room=room_name)
        await lkapi.room.delete_room(delete_request)
        logger.info(f"Successfully deleted room '{room_name}' from LiveKit.")

        if db_room:
            db.delete(db_room)
            db.commit()
            logger.info(f"Successfully deleted room '{room_name}' from local database.")

    except Exception as e:
        logger.error(f"Error during LiveKit room deletion for '{room_name}': {e}")


async def close_livekit_client():
    """Gracefully closes the LiveKit API client."""
    await lkapi.aclose()
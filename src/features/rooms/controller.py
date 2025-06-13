# src/features/rooms/controller.py (Updated)
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from src.database.core import get_db
from src.features.rooms import service as room_service
from src.features.rooms import models as room_models
from src.exceptions import RoomNotFoundException, RoomAlreadyExistsException, LiveKitServiceException

router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/",
    response_model=room_models.RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new meeting room",
)
async def create_room(
    request: room_models.RoomCreateRequest,
    db: Session = Depends(get_db)
):
    try:
        db_room = await room_service.create_room_service(db=db, request=request)
        return db_room
    except (RoomAlreadyExistsException, LiveKitServiceException) as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post(
    "/{room_name}/token",
    response_model=room_models.JoinTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a join token for a room",
)
def create_join_token(
    room_name: str,
    request: room_models.JoinTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        jwt = room_service.create_join_token_service(db=db, room_name=room_name, request=request)
        return room_models.JoinTokenResponse(token=jwt)
    except RoomNotFoundException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while generating the token: {str(e)}"
        )

# --- NEW ENDPOINT ---
@router.delete(
    "/{room_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a meeting room",
    description="Deletes a room from the LiveKit server and removes its record from the local database."
)
async def delete_room(room_name: str, db: Session = Depends(get_db)):
    try:
        await room_service.delete_room_service(db=db, room_name=room_name)
        # For DELETE, a 204 response means success and has no body.
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        # Even if deletion fails, we don't want to show a scary error to the user leaving a call.
        # In a real app, you'd log this error for monitoring.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to delete the room: {str(e)}"
        )
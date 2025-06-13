from fastapi import HTTPException, status

class RoomNotFoundException(HTTPException):
    """
    Exception raised when a requested room is not found in the database.
    """
    def __init__(self, room_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room '{room_name}' not found."
        )

class RoomAlreadyExistsException(HTTPException):
    """
    Exception raised when attempting to create a room that already exists.
    """
    def __init__(self, room_name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Room '{room_name}' already exists."
        )

class LiveKitServiceException(HTTPException):
    """
    Exception raised for failures when interacting with the LiveKit API.
    """
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LiveKit service error: {detail}"
        )
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Literal

# Define a literal type for access control to enforce specific values.
AccessType = Literal['public', 'token', 'nft']

class RoomBase(BaseModel):
    """
    Base Pydantic model for room data. Contains fields common to both
    creation requests and responses.
    """
    name: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$",
                      description="Unique, URL-friendly name for the room.")
    access_type: AccessType = Field(..., description="Access control type for the room.")
    token_address: Optional[str] = Field(None, description="ERC-20 contract address for token-gated rooms.")
    token_amount: Optional[str] = Field(None, description="Minimum token amount required for token-gated rooms.")
    nft_address: Optional[str] = Field(None, description="NFT contract address for NFT-gated rooms.")

    model_config = ConfigDict(
        from_attributes=True,  # Allow creating Pydantic models from ORM objects
        json_schema_extra={
            "example": {
                "name": "my-cool-meeting",
                "access_type": "public",
                "token_address": None,
                "token_amount": None,
                "nft_address": None
            }
        }
    )

class RoomCreateRequest(RoomBase):
    """
    Pydantic model for the request body when creating a new room.
    Includes additional LiveKit-specific configuration options.
    """
    empty_timeout: int = Field(600, description="Timeout in seconds before an empty room is closed.", gt=0)
    max_participants: int = Field(50, description="Maximum number of participants allowed in the room.", gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "my-dao-meeting",
                "access_type": "token",
                "token_address": "0x...",
                "token_amount": "1000000000000000000",
                "nft_address": None,
                "empty_timeout": 300,
                "max_participants": 20
            }
        }
    )

class RoomResponse(RoomBase):
    """
    Pydantic model for the API response when a room is created or fetched.
    Includes database-generated fields like `id` and `created_at`.
    """
    id: int
    livekit_sid: str = Field(..., description="The Server ID (SID) from the LiveKit server.")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "my-dao-meeting",
                "livekit_sid": "RM_xxxxxxxxx",
                "access_type": "token",
                "token_address": "0x...",
                "token_amount": "1000000000000000000",
                "nft_address": None,
                "created_at": "2024-01-01T12:00:00Z"
            }
        }
    )


class JoinTokenRequest(BaseModel):
    """
    Pydantic model for the request body to generate a join token.
    Requires a unique identity and a display name for the participant.
    """
    identity: str = Field(..., description="Unique identifier for the participant (e.g., wallet address).")
    name: str = Field(..., description="Display name for the participant in the meeting.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity": "0x1234...abcd",
                "name": "Alice"
            }
        }
    )

class JoinTokenResponse(BaseModel):
    """
    Pydantic model for the API response containing the generated JWT access token.
    """
    token: str = Field(..., description="The JWT access token for joining a LiveKit room.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )
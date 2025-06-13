from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from src.database.core import Base

class Room(Base):
    """
    Represents a meeting room in the database.
    This is the core domain entity that stores persistent information about a room,
    including its configuration and LiveKit server ID.
    """
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # The unique, human-readable name for the room. Used in URLs.
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    # The Server ID (SID) assigned by the LiveKit server upon creation.
    livekit_sid: Mapped[str] = mapped_column(String, nullable=False)

    # Access control type: 'public', 'token', or 'nft'.
    access_type: Mapped[str] = mapped_column(String, nullable=False, default='public')

    # Optional fields for token-gated or NFT-gated rooms.
    # Storing token_amount as a string to handle potential large numbers (e.g., wei).
    token_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    token_amount: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    nft_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Timestamp for when the room record was created.
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}', livekit_sid='{self.livekit_sid}')>"
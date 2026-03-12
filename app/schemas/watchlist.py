"""Pydantic schemas for Watchlist and Watch Log validation."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ── Watchlist Schemas ──────────────────────────────────────────────

class WatchlistCreate(BaseModel):
    """Schema for adding a movie to a watchlist."""
    tmdb_film_id: int = Field(..., description="The TMDB ID of the film")


class WatchlistResponse(WatchlistCreate):
    """Schema for returning a watchlist item."""
    id: int
    user_id: int
    added_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ── Watch Log Schemas ──────────────────────────────────────────────

class WatchLogCreate(BaseModel):
    """Schema for logging a watched movie."""
    tmdb_film_id: int = Field(..., description="The TMDB ID of the film")
    rating: int | None = Field(None, ge=1, le=10, description="Optional rating from 1 to 10")
    review: str | None = Field(None, description="Optional text review")


class WatchLogUpdate(BaseModel):
    """Schema for updating an existing watch log entry."""
    rating: int | None = Field(None, ge=1, le=10)
    review: str | None = Field(None)


class WatchLogResponse(WatchLogCreate):
    """Schema for returning a watch log entry."""
    id: int
    user_id: int
    watched_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

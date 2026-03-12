"""Pydantic schemas for Watchlist and Watch Log validation."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ── Watchlist Schemas ──────────────────────────────────────────────

class WatchlistCreate(BaseModel):
    """Schema for adding a movie to a watchlist."""
    tmdb_id: int = Field(..., description="The TMDB ID of the film")
    title: str = Field(..., description="The title of the film")
    poster_path: str | None = Field(None, description="The URL of the poster image")


class WatchlistResponse(WatchlistCreate):
    """Schema for returning a watchlist item."""
    id: int
    user_id: int
    added_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ── Watch Log Schemas ──────────────────────────────────────────────

class WatchLogCreate(BaseModel):
    """Schema for logging a watched movie."""
    tmdb_id: int = Field(..., description="The TMDB ID of the film")
    title: str = Field(..., description="The title of the film")
    rating: float | None = Field(None, ge=0.5, le=10, description="Optional rating from 0.5 to 10")
    review: str | None = Field(None, description="Optional text review")
    director: str | None = Field(None)
    runtime: int | None = Field(None)


class WatchLogUpdate(BaseModel):
    """Schema for updating an existing watch log entry."""
    rating: float | None = Field(None, ge=0.5, le=10)
    review: str | None = Field(None)


class WatchLogResponse(WatchLogCreate):
    """Schema for returning a watch log entry."""
    id: int
    user_id: int
    logged_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

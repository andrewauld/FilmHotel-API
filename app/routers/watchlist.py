"""
Router for managing watchlists and watch logs.

Requires authentication.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.watchlist import (
    WatchlistCreate, WatchlistResponse,
    WatchLogCreate, WatchLogUpdate, WatchLogResponse
)
from app.services import watchlist as watchlist_service

router = APIRouter(tags=["Watchlist & Log"])

# ── Watchlist Endpoints ─────────────────────────────────────────────

@router.get("/watchlist", response_model=list[WatchlistResponse])
def get_watchlist(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the current user's watchlist."""
    return watchlist_service.get_watchlist(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("/watchlist", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    item_in: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a TMDB film to the watchlist."""
    return watchlist_service.add_to_watchlist(db, user_id=current_user.id, item_in=item_in)


@router.delete("/watchlist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a film from the watchlist by its internal ID."""
    watchlist_service.remove_from_watchlist(db, user_id=current_user.id, item_id=item_id)


# ── Watch Log Endpoints ─────────────────────────────────────────────

@router.get("/log", response_model=list[WatchLogResponse])
def get_watch_history(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the current user's watch history (log)."""
    return watchlist_service.get_watch_log(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("/log", response_model=WatchLogResponse, status_code=status.HTTP_201_CREATED)
def log_watched_film(
    log_in: WatchLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log a film as watched, optionally with a rating (1-10) and a review.
    Automatically removes the film from the user's watchlist if it was present.
    """
    return watchlist_service.log_watched_film(db, user_id=current_user.id, log_in=log_in)


@router.patch("/log/{log_id}", response_model=WatchLogResponse)
def update_watch_log_entry(
    log_id: int,
    log_update: WatchLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the rating or review of an existing watch log entry."""
    return watchlist_service.update_watch_log(
        db, user_id=current_user.id, log_id=log_id, log_update=log_update
    )


@router.delete("/log/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watch_log_entry(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a watch log entry."""
    watchlist_service.delete_watch_log(db, user_id=current_user.id, log_id=log_id)

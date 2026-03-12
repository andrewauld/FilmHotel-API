"""
Services for managing watchlists and watch logs.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.watchlist import WatchlistItem
from app.models.watch_log import WatchLogEntry
from app.schemas.watchlist import WatchlistCreate, WatchLogCreate, WatchLogUpdate


# ── Watchlist Services ──────────────────────────────────────────────

def get_watchlist(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[WatchlistItem]:
    """Get a user's watchlist."""
    return db.query(WatchlistItem).filter(WatchlistItem.user_id == user_id).offset(skip).limit(limit).all()


def add_to_watchlist(db: Session, user_id: int, item_in: WatchlistCreate) -> WatchlistItem:
    """Add a film to a user's watchlist."""
    # Check if already in watchlist
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.tmdb_id == item_in.tmdb_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Film is already in your watchlist"
        )
        
    db_item = WatchlistItem(
        user_id=user_id,
        tmdb_id=item_in.tmdb_id,
        title=item_in.title,
        poster_path=item_in.poster_path
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def remove_from_watchlist(db: Session, user_id: int, item_id: int):
    """Remove a film from a user's watchlist."""
    db_item = db.query(WatchlistItem).filter(
        WatchlistItem.id == item_id,
        WatchlistItem.user_id == user_id
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist item not found")
        
    db.delete(db_item)
    db.commit()


# ── Watch Log Services ──────────────────────────────────────────────

def get_watch_log(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[WatchLogEntry]:
    """Get a user's watch history."""
    return db.query(WatchLogEntry).filter(WatchLogEntry.user_id == user_id).order_by(WatchLogEntry.logged_at.desc()).offset(skip).limit(limit).all()


def log_watched_film(db: Session, user_id: int, log_in: WatchLogCreate) -> WatchLogEntry:
    """Log a film as watched."""
    db_log = WatchLogEntry(
        user_id=user_id,
        tmdb_id=log_in.tmdb_id,
        title=log_in.title,
        rating=log_in.rating,
        review=log_in.review,
        director=log_in.director,
        runtime=log_in.runtime
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    # Optionally remove from watchlist if it was there
    existing_watchlist_item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.tmdb_id == log_in.tmdb_id
    ).first()
    
    if existing_watchlist_item:
        db.delete(existing_watchlist_item)
        db.commit()
        
    return db_log


def update_watch_log(db: Session, user_id: int, log_id: int, log_update: WatchLogUpdate) -> WatchLogEntry:
    """Update a rating or review on an existing watch log entry."""
    db_log = db.query(WatchLogEntry).filter(
        WatchLogEntry.id == log_id,
        WatchLogEntry.user_id == user_id
    ).first()
    
    if not db_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watch log entry not found")
        
    update_data = log_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_log, key, value)
        
    db.commit()
    db.refresh(db_log)
    return db_log


def delete_watch_log(db: Session, user_id: int, log_id: int):
    """Delete a watch log entry."""
    db_log = db.query(WatchLogEntry).filter(
        WatchLogEntry.id == log_id,
        WatchLogEntry.user_id == user_id
    ).first()
    
    if not db_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watch log entry not found")
        
    db.delete(db_log)
    db.commit()

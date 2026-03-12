"""
Services for managing user preferences.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.genre_preference import GenrePreference
from app.schemas.preferences import GenrePreferenceCreate


def get_user_preferences(db: Session, user_id: int) -> list[GenrePreference]:
    """Get all genre preferences for a user."""
    return db.query(GenrePreference).filter(GenrePreference.user_id == user_id).all()


def set_user_preference(db: Session, user_id: int, pref_in: GenrePreferenceCreate) -> GenrePreference:
    """Set or update a genre preference."""
    db_pref = db.query(GenrePreference).filter(
        GenrePreference.user_id == user_id,
        GenrePreference.tmdb_genre_id == pref_in.tmdb_genre_id
    ).first()
    
    if db_pref:
        # Update existing
        db_pref.weight = pref_in.weight
        db_pref.genre_name = pref_in.genre_name
    else:
        # Create new
        db_pref = GenrePreference(
            user_id=user_id,
            tmdb_genre_id=pref_in.tmdb_genre_id,
            genre_name=pref_in.genre_name,
            weight=pref_in.weight
        )
        db.add(db_pref)
        
    db.commit()
    db.refresh(db_pref)
    return db_pref


def delete_user_preference(db: Session, user_id: int, genre_id: int):
    """Delete a genre preference."""
    db_pref = db.query(GenrePreference).filter(
        GenrePreference.user_id == user_id,
        GenrePreference.tmdb_genre_id == genre_id
    ).first()
    
    if not db_pref:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre preference not found")
        
    db.delete(db_pref)
    db.commit()

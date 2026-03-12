"""
Router for managing user genre preferences.

Requires authentication.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.preferences import GenrePreferenceCreate, GenrePreferenceResponse
from app.services import preferences as preferences_service

router = APIRouter(prefix="/preferences", tags=["User Preferences"])


@router.get("", response_model=list[GenrePreferenceResponse])
def get_user_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the current user's genre preferences."""
    return preferences_service.get_user_preferences(db, user_id=current_user.id)


@router.put("", response_model=GenrePreferenceResponse)
def set_user_preference(
    pref_in: GenrePreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Set or update a genre preference.
    Weight should be 1.0 for neutral, >1.0 for liked, and <1.0 for disliked.
    """
    return preferences_service.set_user_preference(db, user_id=current_user.id, pref_in=pref_in)


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_preference(
    genre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a genre preference."""
    preferences_service.delete_user_preference(db, user_id=current_user.id, genre_id=genre_id)

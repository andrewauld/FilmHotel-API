"""
Router for generating AI-powered film recommendations.

Requires authentication.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User
from app.models.watch_log import WatchLogEntry
from app.models.genre_preference import GenrePreference
from app.dependencies import get_current_user
from app.schemas.recommendation import RecommendationResponse
from app.services import gemini as gemini_service

router = APIRouter(prefix="/recommendations", tags=["AI Recommendations"])


def _get_user_profile(db: Session, user_id: int):
    """Helper to extract recent watches, highly rated films, and genre preferences."""
    # 1. Recently watched (last 10)
    recent_logs = db.query(WatchLogEntry).filter(
        WatchLogEntry.user_id == user_id
    ).order_by(desc(WatchLogEntry.logged_at)).limit(10).all()
    recently_watched = [log.title for log in recent_logs]

    # 2. Highly rated (rated 8.0 or higher)
    high_logs = db.query(WatchLogEntry).filter(
        WatchLogEntry.user_id == user_id,
        WatchLogEntry.rating >= 8.0
    ).order_by(desc(WatchLogEntry.rating)).limit(10).all()
    highly_rated = list(set([log.title for log in high_logs])) # Deduplicate if overlaps with recent

    # 3. Preferences (liked vs disliked)
    prefs = db.query(GenrePreference).filter(GenrePreference.user_id == user_id).all()
    favourite_genres = [p.genre_name for p in prefs if p.weight > 1.0]
    disliked_genres = [p.genre_name for p in prefs if p.weight < 1.0]

    return recently_watched, highly_rated, favourite_genres, disliked_genres


@router.get("", response_model=RecommendationResponse)
def get_recommendations(
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get generic personalised recommendations based on your watch history and liked genres.
    """
    recent, highly_rated, favs, _ = _get_user_profile(db, current_user.id)
    
    return gemini_service.get_personalised_recommendations(
        recently_watched=recent,
        highly_rated=highly_rated,
        favourite_genres=favs,
        limit=limit
    )


@router.get("/cross-genre", response_model=RecommendationResponse)
def get_cross_genre_recommendations(
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Push yourself outside your comfort zone. 
    Finds films outside your usual genres but sharing thematic similarities to your highly rated films.
    """
    _, highly_rated, favs, dislikes = _get_user_profile(db, current_user.id)
    
    return gemini_service.get_cross_genre_recommendations(
        highly_rated=highly_rated,
        favourite_genres=favs,
        disliked_genres=dislikes,
        limit=limit
    )

"""
Router for computing and returning user watch analytics.

All endpoints require authentication.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.analytics import (
    AnalyticsSummary,
    DirectorStats,
    GenreStats,
    RatingDistribution,
    TimelineStats
)
from app.services import analytics as analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get high-level statistics: total films, runtime, and average rating."""
    return analytics_service.get_summary_stats(db, user_id=current_user.id)


@router.get("/top-directors", response_model=list[DirectorStats])
def get_top_directors(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return the most-watched directors."""
    return analytics_service.get_top_directors(db, user_id=current_user.id, limit=limit)


@router.get("/genres", response_model=list[GenreStats])
def get_genre_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return the count and average rating for each watched genre."""
    return analytics_service.get_genre_stats(db, user_id=current_user.id)


@router.get("/ratings-distribution", response_model=list[RatingDistribution])
def get_ratings_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return how many films fall into each rating bucket."""
    return analytics_service.get_ratings_distribution(db, user_id=current_user.id)


@router.get("/timeline", response_model=list[TimelineStats])
def get_timeline_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return the volume of films watched per month (YYYY-MM)."""
    return analytics_service.get_timeline_stats(db, user_id=current_user.id)

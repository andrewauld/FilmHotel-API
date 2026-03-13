"""Pydantic schemas for Analytics responses."""

from pydantic import BaseModel, Field


class AnalyticsSummary(BaseModel):
    """Overall watch statistics for a user."""
    total_films: int = Field(..., description="Total number of films logged")
    total_runtime_minutes: int = Field(..., description="Total minutes watched")
    average_rating: float | None = Field(None, description="Average rating given (0.5 to 10)")


class DirectorStats(BaseModel):
    """Statistics for a specific director."""
    director: str = Field(..., description="Name of the director")
    count: int = Field(..., description="Number of films watched by this director")


class GenreStats(BaseModel):
    """Statistics for a specific genre."""
    tmdb_genre_id: str = Field(..., description="TMDB Genre ID (stringified)")
    count: int = Field(..., description="Number of films watched in this genre")
    average_rating: float | None = Field(None, description="Average rating given to films in this genre")


class RatingDistribution(BaseModel):
    """Count of films for a specific rating."""
    rating: float = Field(..., description="The rating value (0.5 to 10)")
    count: int = Field(..., description="Number of films given this rating")


class TimelineStats(BaseModel):
    """Films watched grouped by month."""
    year_month: str = Field(..., description="Format YYYY-MM")
    count: int = Field(..., description="Number of films watched in this month")

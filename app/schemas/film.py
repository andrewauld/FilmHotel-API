"""Pydantic schemas for Film and TMDB data validation and response serialization."""

from pydantic import BaseModel, Field


class Genre(BaseModel):
    """Schema for a film genre."""
    id: int
    name: str


class FilmBasic(BaseModel):
    """Basic film information (used in lists like search results, trending)."""
    id: int
    title: str
    overview: str | None = None
    poster_path: str | None = None
    release_date: str | None = None
    vote_average: float | None = None
    genre_ids: list[int] = Field(default_factory=list)


class FilmDetail(BaseModel):
    """Detailed film information including genres and runtime."""
    id: int
    title: str
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    release_date: str | None = None
    vote_average: float | None = None
    runtime: int | None = None
    genres: list[Genre] = Field(default_factory=list)
    director: str | None = None


class FilmListResponse(BaseModel):
    """Paginated response for a list of films."""
    page: int
    results: list[FilmBasic]
    total_pages: int
    total_results: int

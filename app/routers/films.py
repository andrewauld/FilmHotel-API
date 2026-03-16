"""
Films router.

Exposes endpoints for searching and discovering films via TMDB.
These endpoints are public (no authentication required).
"""

from typing import Literal
from fastapi import APIRouter, Depends, Query, Path

from app.schemas.film import FilmBasic, FilmDetail, FilmListResponse, Genre
from app.services.tmdb import tmdb_client

router = APIRouter(prefix="/films", tags=["Films"])


@router.get("/search", response_model=FilmListResponse)
async def search_films(
    query: str = Query(..., min_length=1, description="Movie title to search for"),
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Search for movies by title via TMDB.
    """
    return await tmdb_client.search_movies(query=query, page=page)


@router.get("/trending", response_model=FilmListResponse)
async def get_trending_films(
    time_window: Literal["day", "week"] = Query("week", description="Trending time window"),
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Get the daily or weekly trending movies.
    """
    return await tmdb_client.get_trending(time_window=time_window, page=page)


@router.get("/genres", response_model=list[Genre])
async def get_film_genres():
    """
    Get the official list of TMDB movie genres.
    """
    return await tmdb_client.get_genres()


@router.get("/discover", response_model=FilmListResponse)
async def discover_films(
    with_genres: str | None = Query(None, description="Comma separated TMDB genre IDs"),
    year: int | None = Query(None, description="Primary release year"),
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Discover movies by genre and/or release year, sorted by popularity.
    """
    return await tmdb_client.discover_movies(with_genres=with_genres, year=year, page=page)


@router.get("/{film_id}", response_model=FilmDetail)
async def get_film_details(
    film_id: int = Path(..., description="The TMDB ID of the film")
):
    """
    Get detailed information about a specific movie, including its director.
    """
    return await tmdb_client.get_movie_details(movie_id=film_id)

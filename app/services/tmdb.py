"""
TMDB API client service.

Handles all communication with The Movie Database (TMDB) API v3
using the asynchronous httpx library.
"""

import httpx
from fastapi import HTTPException, status

from app.config import settings

# Base mapping for image URLs from TMDB
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


class TMDBClient:
    """Async client for the TMDB API."""

    def __init__(self):
        self.api_key = settings.tmdb_api_key
        self.base_url = settings.tmdb_base_url
        self.headers = {
            "accept": "application/json",
            # We pass the API key as a query param instead of Bearer token
            # as it's the simpler standard for TMDB v3
        }

    def _get_params(self, **kwargs) -> dict:
        """Helper to inject the API key into request parameters."""
        params = {"api_key": self.api_key}
        params.update(kwargs)
        # Drop None values to avoid polluting the URL
        return {k: v for k, v in params.items() if v is not None}

    def _format_image_urls(self, obj: dict):
        """Helper to prepend the base URL to poster and backdrop paths."""
        if obj.get("poster_path"):
            obj["poster_path"] = f"{IMAGE_BASE_URL}{obj['poster_path']}"
        if obj.get("backdrop_path"):
            obj["backdrop_path"] = f"{IMAGE_BASE_URL}{obj['backdrop_path']}"
        return obj

    async def _request(self, method: str, endpoint: str, params: dict = None) -> dict:
        """Make an async HTTP request to the TMDB API."""
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="TMDB API key is not configured"
            )

        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method, 
                    url, 
                    params=self._get_params(**(params or {})),
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Map TMDB errors to FastAPI HTTPExceptions
                if e.response.status_code == 404:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found on TMDB")
                elif e.response.status_code == 401:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid TMDB API Key")
                else:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"TMDB API error: {e.response.text}"
                    )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Could not connect to TMDB: {str(e)}"
                )

    async def search_movies(self, query: str, page: int = 1) -> dict:
        """Search for movies by their title."""
        data = await self._request("GET", "/search/movie", params={"query": query, "page": page})
        for item in data.get("results", []):
            self._format_image_urls(item)
        return data

    async def get_movie_details(self, movie_id: int) -> dict:
        """Get detailed information about a movie, including credits to extract the director."""
        data = await self._request("GET", f"/movie/{movie_id}", params={"append_to_response": "credits"})
        
        # Extract director from the crew list
        director = None
        credits = data.pop("credits", {})
        for member in credits.get("crew", []):
            if member.get("job") == "Director":
                director = member.get("name")
                break
                
        data["director"] = director
        return self._format_image_urls(data)

    async def get_trending(self, time_window: str = "week", page: int = 1) -> dict:
        """Get the daily or weekly trending movies."""
        data = await self._request("GET", f"/trending/movie/{time_window}", params={"page": page})
        for item in data.get("results", []):
            self._format_image_urls(item)
        return data

    async def get_genres(self) -> list[dict]:
        """Get the official list of movie genres."""
        data = await self._request("GET", "/genre/movie/list")
        return data.get("genres", [])

    async def discover_movies(self, with_genres: str = None, year: int = None, page: int = 1) -> dict:
        """Discover movies by different types of data like genre or year."""
        params = {"page": page, "sort_by": "popularity.desc"}
        if with_genres:
            params["with_genres"] = with_genres
        if year:
            params["primary_release_year"] = year
            
        data = await self._request("GET", "/discover/movie", params=params)
        for item in data.get("results", []):
            self._format_image_urls(item)
        return data


# Instantiate a singleton to be used across the app
tmdb_client = TMDBClient()

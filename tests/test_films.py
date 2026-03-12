import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.tmdb import TMDBClient

client = TestClient(app)

# Sample TMDB API responses
MOCK_SEARCH_RESPONSE = {
    "page": 1,
    "results": [
        {"id": 27205, "title": "Inception", "overview": "A thief...", "poster_path": "/poster.jpg"}
    ],
    "total_pages": 1,
    "total_results": 1
}

MOCK_DETAIL_RESPONSE = {
    "id": 27205,
    "title": "Inception",
    "overview": "A thief...",
    "director": "Christopher Nolan",
    "genres": [{"id": 28, "name": "Action"}]
}

MOCK_GENRES_RESPONSE = [
    {"id": 28, "name": "Action"},
    {"id": 12, "name": "Adventure"}
]

@pytest.fixture
def mock_tmdb():
    """Fixture to mock the globally instantiated TMDB client in the app."""
    with patch("app.routers.films.tmdb_client", new_callable=AsyncMock) as mock:
        yield mock

def test_search_films(mock_tmdb):
    mock_tmdb.search_movies.return_value = MOCK_SEARCH_RESPONSE
    
    response = client.get("/films/search?query=Inception")
    assert response.status_code == 200
    data = response.json()
    assert data["results"][0]["title"] == "Inception"
    mock_tmdb.search_movies.assert_called_once_with(query="Inception", page=1)

def test_get_film_details(mock_tmdb):
    mock_tmdb.get_movie_details.return_value = MOCK_DETAIL_RESPONSE
    
    response = client.get("/films/27205")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Inception"
    assert data["director"] == "Christopher Nolan"
    mock_tmdb.get_movie_details.assert_called_once_with(film_id=27205)

def test_get_film_genres(mock_tmdb):
    mock_tmdb.get_genres.return_value = MOCK_GENRES_RESPONSE
    
    response = client.get("/films/genres")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Action"
    mock_tmdb.get_genres.assert_called_once()

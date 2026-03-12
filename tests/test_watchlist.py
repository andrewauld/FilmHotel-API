import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.user import User

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_watchlist.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Recreate tables in the test database
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_test_user():
    """Create a user and return their access token for authenticated requests."""
    # First register
    client.post(
        "/auth/register",
        json={"username": "watchlistuser", "email": "watch@example.com", "password": "password123"}
    )
    # Then login
    response = client.post(
        "/auth/login",
        data={"username": "watchlistuser", "password": "password123"}
    )
    token = response.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}

def test_add_to_watchlist(setup_test_user):
    headers = setup_test_user
    response = client.post(
        "/watchlist",
        json={"tmdb_id": 27205, "title": "Inception", "poster_path": "/poster.jpg"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tmdb_id"] == 27205
    assert data["title"] == "Inception"
    assert "id" in data

def test_add_duplicate_to_watchlist(setup_test_user):
    headers = setup_test_user
    response = client.post(
        "/watchlist",
        json={"tmdb_id": 27205, "title": "Inception"},
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Film is already in your watchlist"

def test_get_watchlist(setup_test_user):
    headers = setup_test_user
    response = client.get("/watchlist", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["tmdb_id"] == 27205

def test_log_watched_film(setup_test_user):
    headers = setup_test_user
    response = client.post(
        "/log",
        json={"tmdb_id": 155, "title": "The Dark Knight", "rating": 9, "review": "Incredible film"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tmdb_id"] == 155
    assert data["title"] == "The Dark Knight"
    assert data["rating"] == 9
    assert data["review"] == "Incredible film"

def test_update_watch_log(setup_test_user):
    headers = setup_test_user
    # Get the ID
    log_response = client.get("/log", headers=headers)
    log_id = log_response.json()[0]["id"]
    
    response = client.patch(
        f"/log/{log_id}",
        json={"rating": 10},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 10
    assert data["review"] == "Incredible film" # Should remain unchanged

def test_remove_from_watchlist_and_404(setup_test_user):
    headers = setup_test_user
    # Get the ID of the watchlist item
    watchlist_response = client.get("/watchlist", headers=headers)
    item_id = watchlist_response.json()[0]["id"]
    
    # Delete it
    delete_response = client.delete(f"/watchlist/{item_id}", headers=headers)
    assert delete_response.status_code == 204
    
    # Verify it's gone
    verify_response = client.get("/watchlist", headers=headers)
    assert len(verify_response.json()) == 0

def test_delete_watch_log(setup_test_user):
    headers = setup_test_user
    # Get the ID
    log_response = client.get("/log", headers=headers)
    log_id = log_response.json()[0]["id"]
    
    response = client.delete(f"/log/{log_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify it's gone
    verify_response = client.get("/log", headers=headers)
    assert len(verify_response.json()) == 0

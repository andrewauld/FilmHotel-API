import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_preferences.db"

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
        json={"username": "prefuser", "email": "pref@example.com", "password": "password123"}
    )
    # Then login
    response = client.post(
        "/auth/login",
        data={"username": "prefuser", "password": "password123"}
    )
    token = response.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}

def test_set_preference(setup_test_user):
    headers = setup_test_user
    response = client.put(
        "/preferences",
        json={"tmdb_genre_id": 28, "genre_name": "Action", "weight": 2.5},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tmdb_genre_id"] == 28
    assert data["genre_name"] == "Action"
    assert data["weight"] == 2.5
    assert "id" in data

def test_update_existing_preference(setup_test_user):
    headers = setup_test_user
    response = client.put(
        "/preferences",
        json={"tmdb_genre_id": 28, "genre_name": "Action Hero", "weight": 1.5},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tmdb_genre_id"] == 28
    assert data["genre_name"] == "Action Hero"
    assert data["weight"] == 1.5

def test_get_preferences(setup_test_user):
    headers = setup_test_user
    # Add a second preference
    client.put(
        "/preferences",
        json={"tmdb_genre_id": 12, "genre_name": "Adventure", "weight": 0.5},
        headers=headers
    )
    
    response = client.get("/preferences", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_delete_preference(setup_test_user):
    headers = setup_test_user
    
    # Delete Action preference (id=28)
    response = client.delete("/preferences/28", headers=headers)
    assert response.status_code == 204
    
    # Verify it's gone
    verify_response = client.get("/preferences", headers=headers)
    data = verify_response.json()
    assert len(data) == 1
    assert data[0]["tmdb_genre_id"] == 12

def test_delete_nonexistent_preference(setup_test_user):
    headers = setup_test_user
    response = client.delete("/preferences/999", headers=headers)
    assert response.status_code == 404

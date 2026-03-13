import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.schemas.recommendation import RecommendationResponse, RecommendationItem

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_recommendations.db"

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
        json={"username": "geminiuser", "email": "gemini@example.com", "password": "password123"}
    )
    # Then login
    response = client.post(
        "/auth/login",
        data={"username": "geminiuser", "password": "password123"}
    )
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # We don't seed watched films, but we can verify the API route is correctly handling the inputs
    return headers

@patch("app.routers.recommendations.gemini_service.get_personalised_recommendations")
def test_get_recommendations(mock_get_personal, setup_test_user):
    headers = setup_test_user
    
    mock_get_personal.return_value = RecommendationResponse(
        recommendations=[
            RecommendationItem(title="Inception", reason="You like Nolan.", tmdb_id=27205)
        ]
    )
    
    response = client.get("/recommendations?limit=1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["title"] == "Inception"

@patch("app.routers.recommendations.gemini_service.get_cross_genre_recommendations")
def test_get_cross_genre_recommendations(mock_get_cross, setup_test_user):
    headers = setup_test_user
    
    mock_get_cross.return_value = RecommendationResponse(
        recommendations=[
            RecommendationItem(title="Spirited Away", reason="Pushing beyond pure Action.", tmdb_id=129)
        ]
    )
    
    response = client.get("/recommendations/cross-genre?limit=1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["title"] == "Spirited Away"

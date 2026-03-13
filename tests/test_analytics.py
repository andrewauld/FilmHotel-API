import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_analytics.db"

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
    """Create a user and seed their watch log for analytics."""
    client.post(
        "/auth/register",
        json={"username": "analyticuser", "email": "a@example.com", "password": "password123"}
    )
    response = client.post(
        "/auth/login",
        data={"username": "analyticuser", "password": "password123"}
    )
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Seed Watch Logs
    logs = [
        {"tmdb_id": 1, "title": "Film A", "rating": 8.0, "director": "Director X", "runtime": 120, "genre_ids": "28,12"},
        {"tmdb_id": 2, "title": "Film B", "rating": 6.0, "director": "Director Y", "runtime": 90, "genre_ids": "28"},
        {"tmdb_id": 3, "title": "Film C", "rating": 8.0, "director": "Director X", "runtime": 100, "genre_ids": "35,12"},
        {"tmdb_id": 4, "title": "Film D", "rating": 4.0, "director": "Director Z", "runtime": 150, "genre_ids": "18"},
        {"tmdb_id": 5, "title": "Film E", "rating": 10.0, "director": "Director X", "runtime": 80, "genre_ids": "878"},
    ]
    # To properly simulate saving genres and runtime we need to patch the post request
    # wait log_in schema takes runtime and director, but not genre_ids.
    # We must intercept or update db models manually. For a fast test, we can just POST 
    # and rely on the schemas if they supported genre_ids. Oh wait, WatchLogCreate Schema didn't have genre_ids.
    # I should add genre_ids to WatchLogCreate or just insert directly via SQLAlchemy.
    
    db = TestingSessionLocal()
    from app.models.watch_log import WatchLogEntry
    from app.models.user import User
    
    user = db.query(User).filter_by(username="analyticuser").first()
    for log in logs:
        entry = WatchLogEntry(
            user_id=user.id,
            tmdb_id=log["tmdb_id"],
            title=log["title"],
            rating=log["rating"],
            director=log["director"],
            runtime=log["runtime"],
            genre_ids=log["genre_ids"]
        )
        db.add(entry)
    db.commit()
    db.close()
    
    return headers

def test_get_summary(setup_test_user):
    headers = setup_test_user
    response = client.get("/analytics/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_films"] == 5
    assert data["total_runtime_minutes"] == (120 + 90 + 100 + 150 + 80) # 540
    assert data["average_rating"] == (8+6+8+4+10)/5 # 7.2

def test_get_top_directors(setup_test_user):
    headers = setup_test_user
    response = client.get("/analytics/top-directors", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data[0]["director"] == "Director X"
    assert data[0]["count"] == 3
    assert len(data) == 3

def test_get_genres(setup_test_user):
    headers = setup_test_user
    response = client.get("/analytics/genres", headers=headers)
    assert response.status_code == 200
    data = response.json()
    # Genre 28 has Film A(8.0) and Film B(6.0) => avg 7.0, count 2
    # Find genre "28"
    genre_28 = next((g for g in data if g["tmdb_genre_id"] == "28"), None)
    assert genre_28 is not None
    assert genre_28["count"] == 2
    assert genre_28["average_rating"] == 7.0
    
    genre_12 = next((g for g in data if g["tmdb_genre_id"] == "12"), None)
    assert genre_12 is not None
    assert genre_12["count"] == 2
    assert genre_12["average_rating"] == 8.0 # Both A(8) and C(8)

def test_get_ratings_distribution(setup_test_user):
    headers = setup_test_user
    response = client.get("/analytics/ratings-distribution", headers=headers)
    assert response.status_code == 200
    data = response.json()
    # ratings: 8.0(qty 2), 6.0(qty 1), 4.0(qty 1), 10.0(qty 1)
    rating_8 = next(r for r in data if r["rating"] == 8.0)
    assert rating_8["count"] == 2

def test_get_timeline(setup_test_user):
    headers = setup_test_user
    response = client.get("/analytics/timeline", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["count"] == 5

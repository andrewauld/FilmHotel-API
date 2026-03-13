"""
Services for computing user watch history analytics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract

from app.models.watch_log import WatchLogEntry


def get_summary_stats(db: Session, user_id: int) -> dict:
    """Calculate total films, total runtime, and average rating."""
    result = db.query(
        func.count(WatchLogEntry.id).label("total_films"),
        func.sum(WatchLogEntry.runtime).label("total_runtime"),
        func.avg(WatchLogEntry.rating).label("avg_rating")
    ).filter(
        WatchLogEntry.user_id == user_id
    ).first()
    
    return {
        "total_films": result.total_films or 0,
        "total_runtime_minutes": result.total_runtime or 0,
        "average_rating": round(result.avg_rating, 2) if result.avg_rating else None
    }


def get_top_directors(db: Session, user_id: int, limit: int = 5) -> list[dict]:
    """Get the most-watched directors."""
    results = db.query(
        WatchLogEntry.director,
        func.count(WatchLogEntry.id).label("count")
    ).filter(
        WatchLogEntry.user_id == user_id,
        WatchLogEntry.director.isnot(None),
        WatchLogEntry.director != ""
    ).group_by(
        WatchLogEntry.director
    ).order_by(
        desc("count")
    ).limit(limit).all()
    
    return [{"director": r.director, "count": r.count} for r in results]


def get_genre_stats(db: Session, user_id: int) -> list[dict]:
    """
    Get watch count and average rating per genre.
    Note: genre_ids is a comma-separated string in the DB (e.g., "28,12,878").
    We fetch all entries and process them in Python for simplicity, as 
    splitting comma-separated strings in SQL is dialect-specific.
    """
    entries = db.query(WatchLogEntry.genre_ids, WatchLogEntry.rating).filter(
        WatchLogEntry.user_id == user_id,
        WatchLogEntry.genre_ids.isnot(None),
        WatchLogEntry.genre_ids != ""
    ).all()
    
    genre_data = {}
    for entry in entries:
        genres = entry.genre_ids.split(",")
        for g in genres:
            g = g.strip()
            if not g:
                continue
                
            if g not in genre_data:
                genre_data[g] = {"count": 0, "rating_sum": 0.0, "rated_count": 0}
                
            genre_data[g]["count"] += 1
            if entry.rating is not None:
                genre_data[g]["rating_sum"] += entry.rating
                genre_data[g]["rated_count"] += 1
                
    result = []
    for g, data in genre_data.items():
        avg_rating = None
        if data["rated_count"] > 0:
            avg_rating = round(data["rating_sum"] / data["rated_count"], 2)
            
        result.append({
            "tmdb_genre_id": g,
            "count": data["count"],
            "average_rating": avg_rating
        })
        
    # Sort by count descending
    result.sort(key=lambda x: x["count"], reverse=True)
    return result


def get_ratings_distribution(db: Session, user_id: int) -> list[dict]:
    """Get the distribution of user ratings."""
    results = db.query(
        WatchLogEntry.rating,
        func.count(WatchLogEntry.id).label("count")
    ).filter(
        WatchLogEntry.user_id == user_id,
        WatchLogEntry.rating.isnot(None)
    ).group_by(
        WatchLogEntry.rating
    ).order_by(
        desc(WatchLogEntry.rating)
    ).all()
    
    return [{"rating": r.rating, "count": r.count} for r in results]


def get_timeline_stats(db: Session, user_id: int) -> list[dict]:
    """Get films watched grouped by YYYY-MM."""
    # We use string formatting for SQLite compatibility where strftime is needed
    # Using python processing for cross-database compatibility
    entries = db.query(WatchLogEntry.logged_at).filter(
        WatchLogEntry.user_id == user_id
    ).all()
    
    timeline = {}
    for entry in entries:
        month_key = entry.logged_at.strftime("%Y-%m")
        timeline[month_key] = timeline.get(month_key, 0) + 1
        
    result = [{"year_month": k, "count": v} for k, v in timeline.items()]
    result.sort(key=lambda x: x["year_month"])
    
    return result

"""
Services for interacting with Google's Gemini AI to provide film recommendations.
"""

import json
from google import genai
from google.genai import types

from app.config import settings
from app.schemas.recommendation import RecommendationResponse, RecommendationItem

# Initialize the GenAI client if the key is available
# In a real app we might handle missing keys more gracefully, but here we expect it from config
client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

def get_personalised_recommendations(
    recently_watched: list[str], 
    highly_rated: list[str], 
    favourite_genres: list[str],
    limit: int = 5
) -> RecommendationResponse:
    """Generate generic personalised recommendations based on history."""
    if not client:
        # Fallback or stub if no API key is set
        return RecommendationResponse(recommendations=[])

    prompt = f"""
    You are an expert film critic and recommendation engine. 
    Based on the following user profile, recommend {limit} films they should watch next.
    
    Recently Watched: {', '.join(recently_watched) if recently_watched else 'None'}
    Highly Rated Films by User: {', '.join(highly_rated) if highly_rated else 'None'}
    Favourite Genres: {', '.join(favourite_genres) if favourite_genres else 'None'}
    
    Do NOT recommend films that are already in the 'Recently Watched' or 'Highly Rated' lists.
    Provide the response strictly as a JSON object matching this schema:
    {{
      "recommendations": [
        {{
          "title": "Film Title",
          "reason": "Why the user might like it based on their profile",
          "tmdb_id": 12345
        }}
      ]
    }}
    Try your best to provide the accurate TMDB ID. Return ONLY JSON, no markdown formatting.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    try:
        data = json.loads(response.text)
        return RecommendationResponse(**data)
    except Exception as e:
        # Fallback on parsing error
        return RecommendationResponse(recommendations=[])

def get_cross_genre_recommendations(
    highly_rated: list[str], 
    favourite_genres: list[str],
    disliked_genres: list[str],
    limit: int = 5
) -> RecommendationResponse:
    """Generate recommendations outside the user's usual genres, but tuned to their tastes."""
    if not client:
        return RecommendationResponse(recommendations=[])

    prompt = f"""
    You are an expert film critic and recommendation engine. 
    I want to push the user outside of their comfort zone. They usually like:
    Favourite Genres: {', '.join(favourite_genres) if favourite_genres else 'None'}
    Highly Rated Films: {', '.join(highly_rated) if highly_rated else 'None'}
    
    However, they explicitly dislike:
    Disliked Genres: {', '.join(disliked_genres) if disliked_genres else 'None'}
    
    Recommend {limit} films that belong to genres they don't usually watch BUT share 
    thematic elements, pacing, or directorial styles with their highly rated films.
    Absolutely do NOT recommend films from their explicitly Disliked Genres.
    
    Provide the response strictly as a JSON object matching this schema:
    {{
      "recommendations": [
        {{
          "title": "Film Title",
          "reason": "Why the user might like it despite it being outside their usual genres",
          "tmdb_id": 12345
        }}
      ]
    }}
    Try your best to provide the accurate TMDB ID. Return ONLY JSON, no markdown formatting.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    try:
        data = json.loads(response.text)
        return RecommendationResponse(**data)
    except Exception as e:
        # Fallback on parsing error
        return RecommendationResponse(recommendations=[])

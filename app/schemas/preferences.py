"""Pydantic schemas for User preferences validation."""

from pydantic import BaseModel, Field, ConfigDict

class GenrePreferenceCreate(BaseModel):
    """Schema for setting a genre preference."""
    tmdb_genre_id: int = Field(..., description="The TMDB ID of the genre")
    genre_name: str = Field(..., description="The name of the genre (e.g. 'Action')")
    weight: float = Field(
        1.0, 
        ge=0.0, 
        le=5.0, 
        description="Weight indicating how much the user likes this genre. 1 is neutral, >1 is liked, <1 is disliked."
    )

class GenrePreferenceResponse(GenrePreferenceCreate):
    """Schema for returning a genre preference."""
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)

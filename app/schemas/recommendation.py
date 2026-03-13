"""Pydantic schemas for AI recommendations."""

from pydantic import BaseModel, Field

class RecommendationItem(BaseModel):
    """A single film recommendation from the AI."""
    title: str = Field(..., description="The title of the recommended film")
    reason: str = Field(..., description="A short explanation of why it is recommended based on user preferences")
    tmdb_id: int | None = Field(None, description="The TMDB ID of the film, if the AI can provide it")


class RecommendationResponse(BaseModel):
    """The full list of AI recommendations."""
    recommendations: list[RecommendationItem] = Field(..., description="The list of film recommendations")

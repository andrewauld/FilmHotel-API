"""GenrePreference model — per-user genre preferences for recommendation tuning."""

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GenrePreference(Base):
    __tablename__ = "genre_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tmdb_genre_id: Mapped[int] = mapped_column(Integer, nullable=False)
    genre_name: Mapped[str] = mapped_column(String(100), nullable=False)        # e.g. "Science Fiction"
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)   # >1 = favourite, <1 = less interested

    # ── Relationships ─────────────────────────────────
    user = relationship("User", back_populates="genre_preferences")

    def __repr__(self) -> str:
        return f"<GenrePreference(genre='{self.genre_name}', weight={self.weight})>"

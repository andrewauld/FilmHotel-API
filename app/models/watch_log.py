"""WatchLogEntry model — films the user has actually watched, with ratings."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WatchLogEntry(Base):
    __tablename__ = "watch_log_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tmdb_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    genre_ids: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)       # Comma-separated TMDB genre IDs
    director: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    runtime: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)              # Minutes
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)               # 0.5–10 (half-star)
    review: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    watched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────
    user = relationship("User", back_populates="watch_log_entries")

    def __repr__(self) -> str:
        return f"<WatchLogEntry(id={self.id}, title='{self.title}', rating={self.rating})>"

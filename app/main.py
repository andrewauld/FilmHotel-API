"""
FilmHotel API — FastAPI application entry point.

A Film & TV Discovery API with TMDB integration, user watchlists,
watch logging, analytics, and AI-powered recommendations via Google Gemini.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, films, watchlist

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A Film & TV Discovery API. Search films via TMDB, maintain watchlists, "
        "log what you've watched, rate films, explore analytics (top directors, "
        "genre breakdowns), and get AI-powered personalised recommendations."
    ),
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc alternative
)

# ── Include routers ───────────────────────────────────
app.include_router(auth.router)
app.include_router(films.router)
app.include_router(watchlist.router)

# ── CORS middleware ───────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ──────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """Health check / welcome endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}

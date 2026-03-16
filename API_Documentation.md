---
title: "FilmHotel API — Documentation"
author: "Andrew Auld"
date: "March 2026"
geometry: margin=2.5cm
fontsize: 11pt
---

# FilmHotel API Documentation

**Base URL:** `https://filmhotel-api.onrender.com`

**Version:** 1.0.0

FilmHotel is a Film & TV Discovery RESTful API. It allows users to search for films via The Movie Database (TMDB), maintain personal watchlists, log films they have watched with ratings and reviews, explore their viewing analytics, and receive AI-powered personalised recommendations via Google Gemini.

---

## Authentication

All protected endpoints require a valid **JWT Bearer Token** in the `Authorization` header.

```
Authorization: Bearer <your_access_token>
```

Tokens are obtained by logging in via the `/auth/login` endpoint.

---

## 1. Health Check

### `GET /`

Returns basic API information.

**Auth Required:** No

**Response:**
```json
{
  "message": "Welcome to FilmHotel API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### `GET /health`

Simple health check.

**Auth Required:** No

**Response:**
```json
{
  "status": "healthy"
}
```

---

## 2. Authentication Endpoints

### `POST /auth/register`

Register a new user account.

**Auth Required:** No

**Request Body (JSON):**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `username` | string | Yes | 3–50 characters |
| `email` | string | Yes | Valid email format |
| `password` | string | Yes | Minimum 8 characters |

**Example Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2026-03-16T12:00:00Z"
}
```

**Error Responses:**

- `400` — Username or email already registered.

---

### `POST /auth/login`

Log in and receive a JWT access token. Uses OAuth2 password form.

**Auth Required:** No

**Request Body (form-data):**

| Field | Type | Required |
|-------|------|----------|
| `username` | string | Yes |
| `password` | string | Yes |

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Error Responses:**

- `401` — Incorrect username or password.

---

### `GET /auth/me`

Retrieve the currently authenticated user's profile.

**Auth Required:** Yes

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2026-03-16T12:00:00Z"
}
```

**Error Responses:**

- `401` — Missing or invalid token.

---

## 3. Films Endpoints (TMDB Proxy)

These endpoints proxy requests to The Movie Database (TMDB) API and return cleaned responses. No authentication is required.

### `GET /films/search`

Search for films by title.

**Auth Required:** No

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | — | Movie title to search for (min 1 char) |
| `page` | integer | No | 1 | Page number (≥ 1) |

**Response (200 OK):**
```json
{
  "page": 1,
  "results": [
    {
      "id": 27205,
      "title": "Inception",
      "overview": "A thief who steals corporate secrets...",
      "poster_path": "https://image.tmdb.org/t/p/w500/poster.jpg",
      "release_date": "2010-07-16",
      "vote_average": 8.4,
      "genre_ids": [28, 878, 12]
    }
  ],
  "total_pages": 1,
  "total_results": 1
}
```

---

### `GET /films/{film_id}`

Get detailed information about a specific film, including its director.

**Auth Required:** No

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `film_id` | integer | The TMDB ID of the film |

**Response (200 OK):**
```json
{
  "id": 27205,
  "title": "Inception",
  "overview": "A thief who steals corporate secrets...",
  "poster_path": "https://image.tmdb.org/t/p/w500/poster.jpg",
  "backdrop_path": "https://image.tmdb.org/t/p/w500/backdrop.jpg",
  "release_date": "2010-07-16",
  "vote_average": 8.4,
  "runtime": 148,
  "genres": [
    { "id": 28, "name": "Action" },
    { "id": 878, "name": "Science Fiction" }
  ],
  "director": "Christopher Nolan"
}
```

**Error Responses:**

- `404` — Film not found on TMDB.

---

### `GET /films/trending`

Get trending films for the day or week.

**Auth Required:** No

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `time_window` | string | No | `week` | Either `day` or `week` |
| `page` | integer | No | 1 | Page number |

**Response:** Same paginated format as `/films/search`.

---

### `GET /films/genres`

Get the official list of TMDB movie genres.

**Auth Required:** No

**Response (200 OK):**
```json
[
  { "id": 28, "name": "Action" },
  { "id": 12, "name": "Adventure" },
  { "id": 35, "name": "Comedy" }
]
```

---

### `GET /films/discover`

Discover films filtered by genre and/or release year.

**Auth Required:** No

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `with_genres` | string | No | — | Comma-separated TMDB genre IDs |
| `year` | integer | No | — | Primary release year |
| `page` | integer | No | 1 | Page number |

**Response:** Same paginated format as `/films/search`.

---

## 4. Watchlist Endpoints

Manage the authenticated user's personal watchlist.

### `GET /watchlist`

Retrieve the current user's watchlist.

**Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of items to skip |
| `limit` | integer | 100 | Maximum items to return |

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "tmdb_id": 27205,
    "title": "Inception",
    "poster_path": "https://image.tmdb.org/t/p/w500/poster.jpg",
    "added_at": "2026-03-16T12:00:00Z"
  }
]
```

---

### `POST /watchlist`

Add a film to the watchlist.

**Auth Required:** Yes

**Request Body (JSON):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tmdb_id` | integer | Yes | The TMDB ID of the film |
| `title` | string | Yes | The title of the film |
| `poster_path` | string | No | URL of the poster image |

**Response (201 Created):** Returns the created watchlist item.

**Error Responses:**

- `400` — Film already on watchlist.

---

### `DELETE /watchlist/{item_id}`

Remove a film from the watchlist.

**Auth Required:** Yes

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `item_id` | integer | Internal ID of the watchlist item |

**Response:** `204 No Content`

**Error Responses:**

- `404` — Item not found.

---

## 5. Watch Log Endpoints

Log films as watched, with optional ratings and reviews.

### `GET /log`

Retrieve the current user's watch history.

**Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of items to skip |
| `limit` | integer | 100 | Maximum items to return |

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "tmdb_id": 27205,
    "title": "Inception",
    "rating": 9.0,
    "review": "Absolutely mind-bending!",
    "director": "Christopher Nolan",
    "runtime": 148,
    "logged_at": "2026-03-16T12:00:00Z"
  }
]
```

---

### `POST /log`

Log a film as watched. If the film is on the user's watchlist, it is automatically removed.

**Auth Required:** Yes

**Request Body (JSON):**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `tmdb_id` | integer | Yes | — | The TMDB film ID |
| `title` | string | Yes | — | The title of the film |
| `rating` | float | No | 0.5 – 10.0 | User rating (half-star increments) |
| `review` | string | No | — | Optional text review |
| `director` | string | No | — | Director name |
| `runtime` | integer | No | — | Runtime in minutes |

**Response (201 Created):** Returns the created log entry.

---

### `PATCH /log/{log_id}`

Update the rating or review of an existing watch log entry.

**Auth Required:** Yes

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `log_id` | integer | ID of the watch log entry |

**Request Body (JSON):**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `rating` | float | No | 0.5 – 10.0 |
| `review` | string | No | — |

**Response (200 OK):** Returns the updated log entry.

**Error Responses:**

- `404` — Log entry not found.

---

### `DELETE /log/{log_id}`

Delete a watch log entry.

**Auth Required:** Yes

**Response:** `204 No Content`

---

## 6. User Preferences Endpoints

Manage genre preferences used by the recommendation engine.

### `GET /preferences`

Retrieve the current user's genre preferences.

**Auth Required:** Yes

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "tmdb_genre_id": 28,
    "genre_name": "Action",
    "weight": 2.0
  },
  {
    "id": 2,
    "user_id": 1,
    "tmdb_genre_id": 27,
    "genre_name": "Horror",
    "weight": 0.5
  }
]
```

---

### `PUT /preferences`

Set or update a genre preference. If the genre already exists for the user, it is updated.

**Auth Required:** Yes

**Request Body (JSON):**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `tmdb_genre_id` | integer | Yes | — | The TMDB genre ID |
| `genre_name` | string | Yes | — | Name of the genre (e.g., "Action") |
| `weight` | float | No | 0.0 – 5.0 | 1.0 = neutral, >1 = liked, <1 = disliked |

**Response (200 OK):** Returns the created or updated preference object.

---

### `DELETE /preferences/{genre_id}`

Delete a genre preference.

**Auth Required:** Yes

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `genre_id` | integer | The TMDB genre ID to remove |

**Response:** `204 No Content`

**Error Responses:**

- `404` — Preference not found.

---

## 7. Analytics Endpoints

All analytics are scoped to the authenticated user's watch history.

### `GET /analytics/summary`

Get high-level statistics.

**Auth Required:** Yes

**Response (200 OK):**
```json
{
  "total_films": 42,
  "total_runtime_minutes": 5460,
  "average_rating": 7.8
}
```

---

### `GET /analytics/top-directors`

Get the most-watched directors, ranked by count.

**Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 5 | Number of directors to return |

**Response (200 OK):**
```json
[
  { "director": "Christopher Nolan", "count": 5 },
  { "director": "Denis Villeneuve", "count": 3 }
]
```

---

### `GET /analytics/genres`

Get watch count and average rating per genre.

**Auth Required:** Yes

**Response (200 OK):**
```json
[
  { "tmdb_genre_id": "28", "count": 12, "average_rating": 7.5 },
  { "tmdb_genre_id": "878", "count": 8, "average_rating": 8.2 }
]
```

---

### `GET /analytics/ratings-distribution`

Get the distribution of the user's given ratings.

**Auth Required:** Yes

**Response (200 OK):**
```json
[
  { "rating": 10.0, "count": 3 },
  { "rating": 8.0, "count": 7 },
  { "rating": 6.0, "count": 5 }
]
```

---

### `GET /analytics/timeline`

Get the number of films watched per month.

**Auth Required:** Yes

**Response (200 OK):**
```json
[
  { "year_month": "2026-01", "count": 5 },
  { "year_month": "2026-02", "count": 8 },
  { "year_month": "2026-03", "count": 12 }
]
```

---

## 8. AI Recommendation Endpoints

Powered by **Google Gemini**. The AI analyses the user's watch history, ratings, and genre preferences to generate personalised film suggestions.

### `GET /recommendations`

Get personalised recommendations based on watch history and genre preferences.

**Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `limit` | integer | 5 | 1 – 10 | Number of recommendations |

**Response (200 OK):**
```json
{
  "recommendations": [
    {
      "title": "Interstellar",
      "reason": "Based on your love for mind-bending sci-fi like Inception and Arrival.",
      "tmdb_id": 157336
    },
    {
      "title": "Blade Runner 2049",
      "reason": "Denis Villeneuve is one of your most-watched directors.",
      "tmdb_id": 335984
    }
  ]
}
```

---

### `GET /recommendations/cross-genre`

Get recommendations outside the user's usual genres, but thematically aligned with their highly rated films.

**Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `limit` | integer | 5 | 1 – 10 | Number of recommendations |

**Response (200 OK):**
```json
{
  "recommendations": [
    {
      "title": "Spirited Away",
      "reason": "While outside your usual Action genre, its rich world-building and pacing match your top-rated films.",
      "tmdb_id": 129
    }
  ]
}
```

---

## Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "detail": "Description of the error"
}
```

**Common HTTP Status Codes:**

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Resource created |
| `204` | No content (successful deletion) |
| `400` | Bad request (validation error or duplicate) |
| `401` | Unauthorised (missing/invalid token) |
| `404` | Resource not found |
| `422` | Unprocessable entity (schema validation failure) |
| `500` | Internal server error |
| `502` | Bad gateway (TMDB API error) |
| `503` | Service unavailable (cannot reach TMDB) |

---

## Interactive Documentation

The API also provides auto-generated interactive documentation:

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI JSON Schema:** `/openapi.json`

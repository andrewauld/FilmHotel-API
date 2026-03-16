# FilmHotel API

A sophisticated Film & TV Discovery API built with **FastAPI**, **SQLAlchemy**, and integrated with **TMDB** and **Google Gemini AI**. 

This application allows users to search for films, maintain watchlists, log what they have watched with ratings and reviews, declare genre preferences, and receive highly personalised, AI-driven movie recommendations (including cross-genre discovery).

## Features

- **Authentication**: JWT-based user registration and login.
- **TMDB Proxy**: Search films, get trending movies, and fetch metadata without exposing API keys on the client side.
- **Watchlists & Watch Logs**: Full CRUD operations for managing what users want to watch and what they have seen.
- **User Preferences**: Positive and negative weighting for favourite or disliked genres.
- **Analytics Engine**: Extract watch history insights like most-watched directors, average ratings, and genre distributions.
- **AI Recommendations**: Leverage Google Gemini to suggest films tailored exactly to your watch history and preferences.

## Technology Stack

- **Framework**: FastAPI
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Testing**: Pytest & HTTPX
- **Authentication**: Passlib (Bcrypt) & Python-JOSE

## Local Development Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed. Ensure you have obtained free API keys for:
- [The Movie Database (TMDB)](https://www.themoviedb.org/settings/api)
- [Google AI Studio (Gemini)](https://aistudio.google.com/apikey)

### 2. Installation
Clone the repository and install the dependencies in a virtual environment.

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and fill in your details.

```bash
cp .env.example .env
```

Make sure you configure `DATABASE_URL`, `TMDB_API_KEY`, and `GEMINI_API_KEY`. For local development, the default SQLite URL (`sqlite:///./filmhotel.db`) is perfect.

### 4. Database Migrations
Create the database tables using Alembic:

```bash
alembic upgrade head
```

### 5. Running the Application
A convenience script `run.sh` is provided. This will automatically activate the virtual environment and start the Uvicorn server.

```bash
./run.sh
```
Alternatively:
```bash
uvicorn app.main:app --reload
```

You can now view the auto-generated interactive OpenAPI documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Testing

To run the full suite of unit tests, use pytest:

```bash
python -m pytest tests/ -v
```

All tests run against isolated in-memory SQLite databases so they will not affect your local `.db` file.

---

## Deployment Guide (PythonAnywhere)

Deploying a FastAPI application to PythonAnywhere requires running the app via ASGI/WSGI. PythonAnywhere officially supports ASGI for paid accounts (using `uvicorn` or `daphne`), but currently limits free accounts to traditional WSGI. However, using a wrapper like `a2wsgi` is an easy workaround if you want to run FastAPI on WSGI.

Assuming you are using a standard Web App setup on PythonAnywhere:

### Step 1: Push Code to Github
Ensure your latest code is pushed to your Github repository. Note: **Do not** push your `.env` file or `filmhotel.db`.

### Step 2: Clone the Repo onto PythonAnywhere
Open a Bash console in PythonAnywhere and clone your repo:
```bash
git clone https://github.com/yourusername/FilmHotel-API.git
cd FilmHotel-API
```

### Step 3: Set up Virtual Environment
Still in the Bash console:
```bash
mkvirtualenv --python=python3.10 filmhotel-venv
pip install -r requirements.txt
pip install a2wsgi  # Required if deploying on WSGI
```

### Step 4: Configure Database and .env
Create your `.env` file directly on PythonAnywhere using `nano .env`. Insert your `SECRET_KEY`, `TMDB_API_KEY` and `GEMINI_API_KEY`. 

Run the migrations to create the database:
```bash
alembic upgrade head
```

### Step 5: Web App Configuration
1. Go to the **Web** tab gracefully in PythonAnywhere.
2. Click **Add a new web app**. Choose **Manual Configuration** (and the correct Python version).
3. Under the **Virtualenv** section, enter the path to the environment you just created (e.g., `/home/yourusername/.virtualenvs/filmhotel-venv`).
4. Click the link to open your **WSGI configuration file**.

### Step 6: WSGI File Modification
Replace the contents of the WSGI configuration file with:

```python
import sys
import os

path = '/home/yourusername/FilmHotel-API'
if path not in sys.path:
    sys.path.append(path)

# Load environment variables manually
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

from app.main import app as fastapi_app
from a2wsgi import ASGIMiddleware

# Convert ASGI (FastAPI) to WSGI
application = ASGIMiddleware(fastapi_app)
```
*(Make sure to replace `yourusername` with your actual PythonAnywhere username)*.

### Step 7: Reload
Save the WSGI file and hit the big green **Reload** button on the Web tab. Your API should now be live!

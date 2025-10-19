# RecipeServer2

This repository contains a Flask-based recipe planner application. The project now ships with a Docker configuration for local development and production-like deployments.

## Prerequisites

- [Docker](https://www.docker.com/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/) v2

## Running with Docker Compose

1. Build and start the container:
   ```bash
   docker compose up --build
   ```
2. Visit the application at [http://localhost:5001](http://localhost:5001).

The Compose configuration mounts the `data/` directory for the SQLite database and `static/pdfs/` for generated PDF files so they persist between container restarts.

## Running with Docker directly

```bash
docker build -t recipeserver2:latest .
docker run -p 5001:5001 \
  -e FLASK_CONFIG=production \
  -e DATABASE_URL=sqlite:///data/recipes.db \
  -e SECRET_KEY=change-me \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/static/pdfs:/app/static/pdfs" \
  recipeserver2:latest
```

## Environment Variables

- `FLASK_CONFIG`: Flask configuration profile to use (`development`, `testing`, `production`). Defaults to `production` in the Docker image.
- `DATABASE_URL`: SQLAlchemy database URI. Defaults to `sqlite:///data/recipes.db`.
- `SECRET_KEY`: Secret key for Flask sessions. Provide a secure value in production environments.

## Development

You can still run the application locally without Docker:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app wsgi run --debug --port 5001
```

## Testing

Install dependencies as above and run:

```bash
pytest
```

FROM python:3.10-slim

# Copy uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy requirements, app and model
COPY pyproject.toml .
COPY uv.lock .
COPY app.py .
COPY resources/models/cpa_regressor.joblib models/cpa_regressor.joblib

# Set the environment variable for the model path
ENV CPA_MODEL_PATH=models/cpa_regressor.joblib

# Install all dependencies
RUN uv sync --frozen --no-dev

# Expose the port
EXPOSE 8000

# Run the app
CMD [".venv/bin/fastapi", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]

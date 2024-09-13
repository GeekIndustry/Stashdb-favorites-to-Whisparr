# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10.7
FROM python:${PYTHON_VERSION}-slim as base

# Set environment variables
ENV DEBUG=False
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy the requirements file into the container and install dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt

# Copy the rest of the source code into the container
COPY . .

# Set ownership of /app to appuser
RUN chown -R appuser:appuser /app

# Switch to the non-privileged user to run the application.
USER appuser

# Expose the Flask app's port
EXPOSE 5000

# Set the default Flask app
ENV FLASK_APP=app.py

# Command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

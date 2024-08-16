# syntax=docker/dockerfile:1

FROM python:3.10-slim

# Set environment variables
ENV DEBUG=False

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=app.py

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

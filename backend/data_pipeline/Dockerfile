FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

ENTRYPOINT ["python", "-m", "gold_pipeline.ingestion"]
CMD ["--start", "2020-01-01", "--output", "data/raw/xauusd.csv"]

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV APP_ENV=production
EXPOSE 5050
HEALTHCHECK --interval=30s --timeout=10s \
  --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5050/health || exit 1
CMD ["gunicorn","--bind","0.0.0.0:5050","--workers","1","app:app"]

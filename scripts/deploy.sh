#!/usr/bin/env bash
set -e

TARGET_ENV="${1:-}"

if [ "$TARGET_ENV" = "dev" ]; then
  docker stop grade-tracker-dev || true
  docker rm grade-tracker-dev || true
  docker build -t grade-tracker:latest .
  docker run -d -p 5050:5050 --name grade-tracker-dev \
    -e APP_ENV=Development grade-tracker:latest
  echo "Dev app: http://localhost:5050"
elif [ "$TARGET_ENV" = "prod" ]; then
  docker stop grade-tracker-prod || true
  docker rm grade-tracker-prod || true
  docker build -t grade-tracker:latest .
  docker run -d -p 80:5050 --name grade-tracker-prod \
    -e APP_ENV=Production grade-tracker:latest
  echo "Prod app: http://localhost:80"
else
  echo "Usage: ./deploy.sh [dev|prod]"
  exit 1
fi

#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE=".env.prod"
COMPOSE_FILE="docker-compose.prod.yml"

cd "$APP_DIR"

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  echo "ERROR: docker compose/docker-compose not found"
  exit 1
fi

echo "==> build and start containers"
$COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build

echo "==> run database migrations"
$COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T backend alembic upgrade head

echo "==> show service status"
$COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps

echo "==> deployment finished"

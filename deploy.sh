#!/bin/sh
set -eu

# Force sane PATH for non-interactive SSH
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Change these only if your names differ
APP_DIR="/volume1/web_apps/eli-care-log"
IMAGE_NAME="eli-care-log:latest"
CONTAINER_NAME="eli-care-log"
HOST_PORT="5050"
CONTAINER_PORT="5000"

# DB bind mount
HOST_DB_DIR="/volume1/web_apps/eli-care-log-data"
CONTAINER_DB_DIR="/app/db"

echo "== cd to repo"
cd "$APP_DIR"

echo "== git pull"
git pull

echo "== stop container if running"
if sudo docker ps -q -f name="^${CONTAINER_NAME}$" | grep -q .; then
  sudo docker stop "$CONTAINER_NAME"
fi

echo "== remove container if exists"
if sudo docker ps -aq -f name="^${CONTAINER_NAME}$" | grep -q .; then
  sudo docker rm "$CONTAINER_NAME"
fi

echo "== build image"
sudo docker build -t "$IMAGE_NAME" .

echo "== run container"
sudo docker run -d \
  --name "$CONTAINER_NAME" \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  -v "${HOST_DB_DIR}:${CONTAINER_DB_DIR}" \
  --restart unless-stopped \
  "$IMAGE_NAME"

echo "== show status"
sudo docker ps -f name="^${CONTAINER_NAME}$"

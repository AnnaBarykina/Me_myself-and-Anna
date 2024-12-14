#!/usr/bin/env bash
set -e

# Имя образа (замените на ваше имя)
IMAGE_NAME="username/your-repo"
# Тег образа
IMAGE_TAG="latest"

# Логин в Docker Hub (предполагается, что DOCKER_USERNAME и DOCKER_PASSWORD заданы)
echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin

# Создать и активировать билд-контекст Buildx, если он ещё не создан
docker buildx create --name multiarch-builder --use || true

# Проверить, что Buildx активен
docker buildx inspect --bootstrap

# Сборка и пуш мультиархитектурного образа
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t "$IMAGE_NAME:$IMAGE_TAG" \
    --push \
    .

echo "Multiarch image $IMAGE_NAME:$IMAGE_TAG successfully built and pushed!"
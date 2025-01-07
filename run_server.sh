#!/bin/bash

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed or not in PATH. Please install Docker and try again."
  exit 1
fi

echo "Docker is installed. Proceeding..."

# Проверка и остановка контейнера
CONTAINER_ID=$(docker ps --filter "name=comics-app-container" -q)

if [ -n "$CONTAINER_ID" ]; then
  echo "Stopping container..."
  docker stop "$CONTAINER_ID" && docker rm "$CONTAINER_ID"
  echo "Container stopped and removed."
else
  echo "Container comics-app-container not found."
fi

# Удаление папки ComicsAppServer
TARGET_DIR="/root/workdirect/ComicsAppServer"

if [ -d "$TARGET_DIR" ]; then
  echo "Removing existing folder: $TARGET_DIR"
  rm -rf "$TARGET_DIR"
else
  echo "Folder $TARGET_DIR does not exist. Proceeding with cloning."
fi

# Клонирование репозитория
REPO_URL="https://github.com/Vedji/ComicsAppServer.git"  # Замените на URL вашего репозитория

echo "Cloning repository from $REPO_URL..."
git clone "$REPO_URL" "$TARGET_DIR"

# Проверка успешности клонирования
if [ $? -ne 0 ]; then
  echo "Failed to clone repository. Exiting."
  exit 1
fi
echo "Repository cloned successfully."

# Копирование config.txt в папку
CONFIG_FILE="config.txt"

if [ -f "$CONFIG_FILE" ]; then
  echo "Copying $CONFIG_FILE to $TARGET_DIR..."
  cp "$CONFIG_FILE" "$TARGET_DIR/"
  echo "Configuration file copied successfully."
else
  echo "Configuration file $CONFIG_FILE not found. Please provide it and try again."
  exit 1
fi

# Переход в папку репозитория
cd "$TARGET_DIR" || exit

# Запуск docker-compose
echo "Starting the application using docker-compose..."
if [ -f "docker-compose.yml" ]; then
  docker-compose up --build -d
  if [ $? -eq 0 ]; then
    echo "Application started successfully!"
  else
    echo "Failed to start the application. Check the logs for details."
    exit 1
  fi
else
  echo "docker-compose.yml not found in $TARGET_DIR. Please ensure it exists and try again."
  exit 1
fi

echo "Script execution completed successfully."
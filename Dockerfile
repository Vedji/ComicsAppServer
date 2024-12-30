# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое локальной директории (включая app.py) в контейнер
COPY . .

# Открываем порт 5000 для Flask
EXPOSE 5000

# Запускаем Flask-приложение
CMD ["python", "main.py"]

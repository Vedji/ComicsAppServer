# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Команда для запуска приложения
CMD ["python", "server/app.py"]

# Используем базовый образ Ubuntu 24
FROM ubuntu:24.04

# Устанавливаем зависимости для Python и pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы приложения в контейнер
COPY app/ /app/

# Устанавливаем зависимости из requirements.txt
RUN pip3 install -r requirements.txt

# Указываем команду запуска
CMD ["python3", "app.py"]

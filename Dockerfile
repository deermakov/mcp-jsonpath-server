FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка Python зависимостей
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/

# Создание директории для логов
RUN mkdir -p /app/logs

# Установка прав на директорию логов
RUN chmod 755 /app/logs

# Экспозиция порта
EXPOSE 3000

# Запуск сервера
CMD ["python", "src/server.py"]
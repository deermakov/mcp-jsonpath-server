# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY main.py .

# Создаем директорию для логов
RUN mkdir -p /app/logs

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Открываем порт (если нужно для внешнего доступа)
# EXPOSE 8000

# Запускаем приложение
CMD ["python", "main.py"]
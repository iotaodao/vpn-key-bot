# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY bot/ ./bot/

# Создаем директорию для данных
RUN mkdir -p /app/data /app/logs

# Устанавливаем права доступа
RUN chmod -R 755 /app

# Создаем пользователя для запуска приложения
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Открываем порт (если потребуется для webhook)
EXPOSE 8080

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('https://api.telegram.org')" || exit 1

# Команда запуска
CMD ["python", "-m", "bot.main"]

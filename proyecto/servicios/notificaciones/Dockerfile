# Microservicio de Notificaciones (API v2) - Flask + Gunicorn
FROM python:3.13-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000", "--workers", "2"]

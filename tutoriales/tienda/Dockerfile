# 1. Usamos una imagen base oficial de Python ligera
FROM python:3.11-slim

# 2. Evitamos que Python escriba archivos .pyc y buffer de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiamos los requerimientos e instalamos dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos el resto del codigo fuente
COPY . /app/

# 6. Comando por defecto al iniciar el contenedor
# Escucha en el puerto 8000 disponible para el mundo (0.0.0.0)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

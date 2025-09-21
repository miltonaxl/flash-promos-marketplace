FROM python:3.11-slim

# Instalar dependencias del sistema y PostGIS
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && rm -rf /var/run/apt/lists/*

# Crear usuario y directorio de trabajo
RUN useradd --create-home --shell /bin/bash app
WORKDIR /app

# Copiar requirements primero para cachear dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Cambiar ownership al usuario app
RUN chown -R app:app /app
USER app

# Exponer puerto y definir comando por defecto
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
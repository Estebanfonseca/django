# Usa una imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Instala ffmpeg y otras dependencias necesarias
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copia los archivos de requisitos
COPY youtube_downloader/requirements.txt .

# Instala las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación al contenedor
COPY . .

# Cambia el directorio de trabajo para que apunte al directorio donde está manage.py
WORKDIR /app/youtube_downloader

# Recopila los archivos estáticos de Django
RUN python manage.py migrate

# Expone el puerto que Django usará (por defecto 8000)
EXPOSE 8000

# Establece el comando por defecto para ejecutar la aplicación
CMD ["gunicorn", "youtube_downloader.wsgi:application", "--bind", "0.0.0.0:8000"]

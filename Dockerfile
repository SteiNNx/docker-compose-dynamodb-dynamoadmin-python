# Usa la imagen base de Python 3.9
FROM python:3.9-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /usr/src/app

# Copia el resto del código fuente al contenedor
COPY .env ./

# Copia el resto del código fuente al contenedor
COPY src/ ./

# Instala las dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 5000
EXPOSE 5000

# Define el comando por defecto para ejecutar la aplicación
CMD ["python", "app.py"]

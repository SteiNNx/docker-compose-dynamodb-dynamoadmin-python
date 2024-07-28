# Usa la imagen base de Python 3.9
FROM python:3.9-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /usr/src/app

# Copia el archivo .env al contenedor
COPY .env ./

# Copia el resto del código fuente al contenedor
COPY src/ ./

# Copia requirements.txt al contenedor e instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 5000
EXPOSE 5000

# Define el comando por defecto para mantener el contenedor en ejecución
CMD ["tail", "-f", "/dev/null"]
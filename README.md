# 🐋🐍 Docker para DynamoDB, DynamoDB Admin y Python: Entorno Local de Desarrollo

Este proyecto configura un entorno local que incluye una base de datos DynamoDB, una interfaz de administración web para DynamoDB y un contenedor Python preparado para ejecutar scripts en DynamoDB.

## Introducción

Este proyecto proporciona un entorno de desarrollo local para trabajar con DynamoDB sin necesidad de conectarse a AWS. Incluye:

- **DynamoDB Local**: Un servidor DynamoDB que se ejecuta en `localhost:8000`.
- **DynamoDB Admin UI**: Una interfaz gráfica para administrar DynamoDB disponible en `localhost:8001`.
- **Contenedor Python**: Un entorno Python para ejecutar scripts que interactúan con DynamoDB, disponible en `localhost:5000`.

## Tabla de Contenidos

- [🐋🐍 Docker para DynamoDB, DynamoDB Admin y Python: Entorno Local de Desarrollo](#-docker-para-dynamodb-dynamodb-admin-y-python-entorno-local-de-desarrollo)
  - [Introducción](#introducción)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Requisitos Previos](#requisitos-previos)
  - [Estructura del Proyecto](#estructura-del-proyecto)
  - [Instrucciones de Configuración](#instrucciones-de-configuración)
  - [Ejecutar Scripts Python](#ejecutar-scripts-python)

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

```bash
project-root/
│
├── .env                            # Variables de entorno para configurar Docker y la aplicación
├── Dockerfile                      # Instrucciones para construir la imagen de Docker de la aplicación Python
├── docker-compose.yml              # Configuración principal para orquestar y levantar la aplicación Python
├── README.md                       # Descripción detallada del proyecto, configuración y uso
│
├── infrastructure/                 # Contiene todo lo necesario para levantar y gestionar el entorno
│   ├── docker/                     # Configuraciones específicas para servicios de Docker
│   │   └── docker-compose.yml      # Configura servicios para levantar DynamoDB y su interfaz de administración
│   └── scripts/                    # Scripts para gestionar el entorno de desarrollo y producción
│       ├── no_run/                 # Scripts utilitarios no destinados a ejecución directa
│       │   └── terminal-utils.sh   # Funciones comunes y utilitarias para otros scripts de bash
│       └── suite-dynamodb-local.sh # Script para iniciar todo el entorno, incluyendo todos los servicios necesarios
│
└── src/                            # Componentes de la aplicación Python
    ├── requirements.txt            # Lista de bibliotecas y dependencias de Python necesarias
    ├── hello_world.py              # Script "Hello World!"
    ├── migration_ttl.py            # [WIP] Script para migrar una tabla a una copia de seguridad y agregar TTL
    └── no_run/                     # Scripts y datos no destinados a ejecución directa en la aplicación principal
        ├── seed_dynamodb.py        # Script para insertar datos iniciales en DynamoDB
        └── db_pago.json            # Datos JSON que se insertan en DynamoDB como datos iniciales o de prueba
```

## Instrucciones de Configuración

Para levantar el entorno, sigue estos pasos:

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/SteiNNx/docker-compose-dynamodb-dynamoadmin-python.git
   cd docker-compose-dynamodb-dynamoadmin-python
   ```

2. **Ejecutar el script de configuración**:

   Utiliza el siguiente comando para iniciar el entorno de Docker:

   ```bash
   sh infrastructure/scripts/suite-dynamodb-local.sh
   ```

   Este script levantará los siguientes contenedores:

   - **DynamoDB Local** en `localhost:8000`
     - **Imagen** `amazon/dynamodb-local:2.4.0`
   - **DynamoDB Admin UI** en `localhost:8001`
     - **Imagen** `aaronshaf/dynamodb-admin:4.6.1`
   - **Contenedor Python** en `localhost:5000`
     - **Imagen** `python:3.9-slim`
     - **Dependencias**
       - flask
       - boto3
       - python-dotenv

## Ejecutar Scripts Python

Una vez que los contenedores estén en funcionamiento, puedes ejecutar scripts Python en el contenedor Python. Para hacerlo:

1. **Accede al contenedor Python**:

   Ejecuta el siguiente comando para abrir una terminal bash dentro del contenedor:

   ```bash
   docker-compose exec app bash
   ```

2. **Ejecuta Script**:

   Ejecuta el script de ejemplo dentro del contenedor:

   ```bash
   python hello_world.py
   ```

   Esto mostrará:

   ```plaintext
   Hello, Docker World!
   ```

3. **Para salir**:

   Escribe `exit` para salir del contenedor:

   ```bash
   exit
   ```

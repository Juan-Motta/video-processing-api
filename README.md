# Video Processing API

## Descripción

Este proyecto es una API REST que permite la carga y procesamiento asincrónico de videos. Los usuarios pueden subir videos, que se almacenarán en el servidor y se procesarán en segundo plano. La API expone varios endpoints para la gestión de videos y el seguimiento del estado de su procesamiento.

## Características

- **Carga de videos**: Permite a los usuarios subir videos en formato MP4.
- **Procesamiento asincrónico**: Los videos cargados son procesados de manera asincrónica.
- **Estado de procesamiento**: Los usuarios pueden consultar el estado del procesamiento de sus videos.
- **Descarga de videos**: Una vez procesados, los videos pueden ser descargados desde la API.

## Tecnologías

- **FastAPI**: Framework principal para construir la API.
- **Celery**: Utilizado para la ejecución de tareas asincrónicas.
- **Redis**: Backend de Celery para gestionar las colas de tareas.
- **PostgreSQL**: Base de datos para almacenar los metadatos de los videos.
- **Docker**: Usado para la contenedorización de la aplicación y sus servicios asociados.
- **Locust**: Utilizado para realizar pruebas de carga y evaluar el rendimiento de la API bajo diferentes niveles de tráfico.

## Requisitos previos

Asegúrate de tener instalados los siguientes requisitos en tu entorno de desarrollo:

- [Python](https://www.python.org/) 3.11 o superior
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Poetry](https://python-poetry.org/) opcional
- [PostgreSQL](https://www.postgresql.org/) en caso de no utilizar docker
- [Redis](https://redis.io/) en caso de no utilizar docker

## Instalación

Las instrucciones de instalacion estan orientadas para sistemas operativos Linux y macOS

### Poetry

1. Clona este repositorio en tu máquina local:

    ```bash
    git clone https://gitlab.com/misw4203-cloud/misw42020-back.git
    
    cd misw42020-back
    ```
2. Instala las dependencias
    ```bash
    poetry install
    ```
3. Configura las variables de entorno en el archivo .env de acuerdo a las conexiones con base de datos entre otros
   ```bash
   cp .env.example .env
   ```
4. Ejecuta las migraciones
   ```bash
   poetry run python manage.py migrate
   ```
5. Ejecuta el servidor principal
   ```bash
   poetry run python manage.py runserver
   ```
6. Ejecuta el worker
   ```bash
   poetry run python manage.py runworker
   ```

### Pip

1. Clona este repositorio en tu máquina local:

    ```bash
    git clone https://gitlab.com/misw4203-cloud/misw42020-back.git
    
    cd misw42020-back
    ```
2. Crea un entorno virtual
   ```bash
   python -m venv venv
   ```
3. Activa el entorno virtual
   ```bash
   source venv/bin/activate
   ```
4. Instala las dependencias
    ```bash
    pip instal -r requirements.txt
    ```
5. Configura las variables de entorno en el archivo .env de acuerdo a las conexiones con base de datos entre otros
   ```bash
   cp .env.example .env
   ```
6. Ejecuta las migraciones
   ```bash
   poetry run python manage.py migrate
   ```
7. Ejecuta el servidor principal
   ```bash
   poetry run python manage.py runserver
   ```
8. Ejecuta el worker
   ```bash
   poetry run python manage.py runworker
   ```

### Docker

Existen dos configurciones de docker una para levantar solo el backend junto con el worker y otra para levatar el backend junto con todos los servicios requeridos (bases de datos)

1. Clona este repositorio en tu máquina local:

    ```bash
    git clone https://gitlab.com/misw4203-cloud/misw42020-back.git
    
    cd misw42020-back
    ```
2. Cambia de directorio dependiendo si se requiere el proyecto con o sin base de datos
   ```bash
   # Sin base de datos
   cd compose/base
   ```
   ```bash
   # Con base de datos
   cd compose/with_db
   ```
3. Contruye y levanta el contenedor
   ```bash
   docker-compose up --build
   ```
4. Ejecuta migraciones, el nombre del contenedor puede variar, para verificar se debe correr el comando `docker ps`
   ```bash
   docker exec -it cloud_app "python manage.py migrate"
   ```
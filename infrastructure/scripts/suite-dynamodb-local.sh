#!/bin/bash
# Autor: Jorge Reyes

# Incluir funciones de utilidad
source infrastructure/scripts/no_run/terminal-utils.sh

# Función para inicializar el contenedor de Python
init_python_container() {
    warning "Inicializando Python Container"
    breakline
    docker-compose down --volumes all --remove-orphans
    docker-compose up --build -d || {
        critical_error "Error al inicializar container python"
    }
    breakline
}

# Función para ejecutar el script de seed en DynamoDB
execute_seed_script() {
    warning "Ejecutando seed_dynamodb.py"
    breakline
    docker-compose exec app python no_run/seed_dynamodb.py || {
        critical_error "Error al ejecutar seed_dynamodb.py"
    }
    breakline
}

# Función para mostrar la información de entorno levantado
display_environment_info() {
    info "Entorno Levantado"
    breakline
    log "DynamoDB -> localhost:8000"
    log "DynamoDB Admin -> localhost:8001"
    log "Python App -> localhost:5000"
    breakline
    info "Para ejecutar script: docker-compose exec app python <nombre_del_script>.py"
    breakline
}

# Inserta Datos a la DB Dynamo
seed_dynamo_db() {
    init_python_container
    execute_seed_script
    display_environment_info
}

# Inicializar y levantar los servicios de Docker
init_suit_local_up() {
    warning "Iniciando Entorno DynamoDB Local"
    breakline
    source_env_vars ".env"
    docker-compose -f ./infrastructure/docker/docker-compose.yml down --volumes all --remove-orphans
    docker-compose -f ./infrastructure/docker/docker-compose.yml up --build -d || {
        critical_error "Error al orquestar infrastructure/docker/docker-compose.yml"
    }
    breakline
}

# Validar Docker y Docker Compose
validate_environment() {
    log "Validando ambiente"
    breakline
    validate_docker
    validate_docker_compose
}

# Función para validar y levantar Docker Compose
docker_compose_up() {
    validate_environment
    init_suit_local_up
}

# Función principal
main() {
    docker_compose_up
    seed_dynamo_db
}

# Llamada a la función principal con los argumentos de línea de comandos
main "$@"

#!/bin/bash
# Autor: Jorge Reyes

# Incluir funciones de utilidad
source infrastructure/scripts/no_run/terminal_utils.sh

# Inicializar y levantar los servicios de Docker
init_suit_local_up() {
    warning "Iniciando Entorno DynamoDB Local"
    breakline
    source_env_vars ".env"

    # Imprimir valores de las variables de entorno para verificación
    echo "DYNAMODB_PORT: $DYNAMODB_PORT"
    echo "DYNAMODB_HOST: $DYNAMODB_HOST"
    echo "DYNAMODB_ADMIN_PORT: $DYNAMODB_ADMIN_PORT"
    echo "DYNAMODB_ADMIN_HOST: $DYNAMODB_ADMIN_HOST"
    echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
    echo "AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY"
    echo "AWS_REGION: $AWS_REGION"
    echo "DYNAMODB_ENDPOINT: $DYNAMODB_ENDPOINT"
    echo "DYNAMODB_ADMIN_ENDPOINT: $DYNAMODB_ADMIN_ENDPOINT"

    docker-compose -f ./infrastructure/docker/docker-compose.yml down --volumes all --remove-orphans
    docker-compose -f ./infrastructure/docker/docker-compose.yml up --build || {
        critical_error "Problemas al iniciar docker-compose.yml"
    }
}

# Función para validar y levantar Docker Compose
docker_compose_up() {
    log "Validando ambiente"
    breakline
    validate_docker
    validate_docker_compose
    init_suit_local_up
    success "todo ok"
}

# Función principal
main() {    
    docker_compose_up
}

# Llamada a la función principal con los argumentos de línea de comandos
main "$@"

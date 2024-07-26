import boto3
from datetime import datetime
import time

# Configuración de AWS
AWS_REGION = 'us-east-1'
TABLE_NAME = 'MiTabla'
BACKUP_TABLE_SUFFIX = '-backup-'
TTL_FIELD_NAME = 'ttl'

# Inicializa el cliente de DynamoDB
dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)

# Función para calcular el TTL en segundos
def calculate_ttl(days=30):
    return int(time.time()) + days * 86400  # 86400 segundos en un día

# Función para obtener los elementos de una tabla
def get_items(table_name):
    response = dynamodb.scan(TableName=table_name)
    items = response.get('Items', [])
    return items

# Función para crear una tabla de respaldo
def create_backup_table():
    backup_table_name = f"{TABLE_NAME}{BACKUP_TABLE_SUFFIX}{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Obtén el esquema de la tabla original
    original_table = dynamodb.describe_table(TableName=TABLE_NAME)
    key_schema = original_table['Table']['KeySchema']
    provisioned_throughput = original_table['Table']['ProvisionedThroughput']
    attribute_definitions = original_table['Table']['AttributeDefinitions']
    
    # Crear la tabla de respaldo
    dynamodb.create_table(
        TableName=backup_table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        ProvisionedThroughput=provisioned_throughput
    )
    
    return backup_table_name

# Función para migrar datos a la tabla de respaldo
def migrate_data(backup_table_name):
    items = get_items(TABLE_NAME)
    
    with dynamodb.batch_writer(TableName=backup_table_name) as batch:
        for item in items:
            batch.put_item(Item=item)
    
    print(f"Datos migrados a {backup_table_name}")

# Función para eliminar la tabla original
def delete_table():
    dynamodb.delete_table(TableName=TABLE_NAME)
    print(f"Tabla {TABLE_NAME} eliminada")

# Función para crear una nueva tabla con TTL habilitado
def create_new_table_with_ttl():
    new_table_name = TABLE_NAME
    
    # Obtener el esquema de la tabla original
    original_table = dynamodb.describe_table(TableName=TABLE_NAME)
    key_schema = original_table['Table']['KeySchema']
    provisioned_throughput = original_table['Table']['ProvisionedThroughput']
    attribute_definitions = original_table['Table']['AttributeDefinitions']
    
    # Crear una nueva tabla con TTL
    dynamodb.create_table(
        TableName=new_table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions + [{'AttributeName': TTL_FIELD_NAME, 'AttributeType': 'N'}],
        ProvisionedThroughput=provisioned_throughput
    )
    
    print(f"Tabla {new_table_name} creada con TTL habilitado")

# Función para habilitar TTL en la nueva tabla
def enable_ttl():
    dynamodb.update_time_to_live(
        TableName=TABLE_NAME,
        TimeToLiveSpecification={
            'Enabled': True,
            'AttributeName': TTL_FIELD_NAME
        }
    )
    
    print(f"TTL habilitado en la tabla {TABLE_NAME}")

# Ejecutar el flujo de trabajo
def main():
    backup_table_name = create_backup_table()
    migrate_data(backup_table_name)
    delete_table()
    create_new_table_with_ttl()
    enable_ttl()

if __name__ == '__main__':
    main()

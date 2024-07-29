import boto3
import os
import logging
from datetime import datetime
import time
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de variables de entorno
DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT', 'http://dynamodb-local:8000')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'fakemykeyid')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'fakemysecretaccesskey')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', 'fakemysessiontoken')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
TABLE_NAME = os.getenv('TABLE_BE_AD_API_POS_PAGOS', 'be-ad-api-pos-pag')
BACKUP_TABLE_SUFFIX = '-backup-'
TTL_FIELD_NAME = 'ttl'
KEY_SCHEMA = [
    {'AttributeName': 'idPago', 'KeyType': 'HASH'},
    {'AttributeName': 'fecha', 'KeyType': 'S'} 
]

# Inicializa el cliente y recurso de DynamoDB
dynamodb_client = boto3.client(
    'dynamodb',
    region_name=AWS_REGION,
    endpoint_url=DYNAMODB_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

dynamodb_resource = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    endpoint_url=DYNAMODB_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Función para calcular el TTL en segundos
def calculate_ttl(days=30):
    # Calcular el TTL en segundos desde la época
    ttl_seconds = int(time.time()) + days * 86400  # 86400 segundos en un día
    # Convertir el valor a una cadena y devolverlo
    return str(ttl_seconds)

# Función para habilitar TTL en la nueva tabla
def enable_ttl():
    dynamodb_resource.update_time_to_live(
        TableName=TABLE_NAME,
        TimeToLiveSpecification={
            'Enabled': True,
            'AttributeName': TTL_FIELD_NAME
        }
    )
    
    print(f"TTL habilitado en la tabla {TABLE_NAME}")

# Función para obtener los elementos de una tabla
def get_items(table_name):
    response = dynamodb_client.scan(TableName=table_name)
    items = response.get('Items', [])
    return items

# Función para crear una tabla de respaldo
def create_backup_table():
    # Nombre de la nueva tabla de respaldo con marca de tiempo
    backup_table_name = f"{TABLE_NAME}{BACKUP_TABLE_SUFFIX}{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    logger.info(f"Creando tabla de respaldo: {backup_table_name}")
    
    # Obtén el esquema de la tabla original
    logger.info(f"Obteniendo detalles de la tabla original: {TABLE_NAME}")
    original_table = dynamodb_client.describe_table(TableName=TABLE_NAME)
    key_schema = KEY_SCHEMA
    provisioned_throughput = original_table['Table']['ProvisionedThroughput']
    attribute_definitions = original_table['Table']['AttributeDefinitions']
    
    logger.info(f"Key Schema: {key_schema}")
    logger.info(f"Provisioned Throughput: {provisioned_throughput}")
    logger.info(f"Attribute Definitions: {attribute_definitions}")

    # Extraer nombres de atributos del KeySchema
    key_attribute_names = {key['AttributeName'] for key in key_schema}
    logger.info(f"Nombres de atributos del KeySchema: {key_attribute_names}")

    # Crear un diccionario de AttributeDefinitions para comprobación
    attribute_definitions_dict = {attr['AttributeName']: attr for attr in attribute_definitions}

    # Verificar que todos los atributos en KeySchema están en AttributeDefinitions
    for key_name in key_attribute_names:
        if key_name not in attribute_definitions_dict:
            logger.info(f"El atributo '{key_name}' no está en AttributeDefinitions, se agregará.")
            attribute_definitions.append({'AttributeName': key_name, 'AttributeType': 'S'})  # Assuming 'S' (String) type

    logger.info(f"Definiciones de atributos actualizadas: {attribute_definitions}")

    # Crear la tabla de respaldo
    logger.info(f"Creando la tabla de respaldo con nombre: {backup_table_name}")
    try:
        dynamodb_client.create_table(
            TableName=backup_table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput={
                'ReadCapacityUnits': provisioned_throughput['ReadCapacityUnits'],
                'WriteCapacityUnits': provisioned_throughput['WriteCapacityUnits']
            }
        )
        logger.info(f"Tabla de respaldo '{backup_table_name}' creada exitosamente")
    except Exception as e:
        logger.error(f"Error al crear la tabla de respaldo: {str(e)}")
        raise

    return backup_table_name

# Función para agregar el atributo TTL a la tabla de respaldo
def add_ttl_attribute(backup_table_name):
    logger.info(f"Agregando atributo TTL '{TTL_FIELD_NAME}' a la tabla de respaldo: {backup_table_name}")

    # Obtén el esquema de la tabla de respaldo
    backup_table = dynamodb_client.describe_table(TableName=backup_table_name)
    attribute_definitions = backup_table['Table']['AttributeDefinitions']

    # Crear un diccionario de AttributeDefinitions para comprobación
    attribute_definitions_dict = {attr['AttributeName']: attr for attr in attribute_definitions}

    # Agregar el atributo TTL a AttributeDefinitions si no está presente
    if TTL_FIELD_NAME not in attribute_definitions_dict:
        logger.info(f"Agregando atributo TTL '{TTL_FIELD_NAME}' a AttributeDefinitions")
        attribute_definitions.append({'AttributeName': TTL_FIELD_NAME, 'AttributeType': 'N'})

        # Actualizar la tabla con el nuevo atributo
        dynamodb_client.update_table(
            TableName=backup_table_name,
            AttributeDefinitions=attribute_definitions
        )

        logger.info(f"Atributo TTL '{TTL_FIELD_NAME}' agregado exitosamente")
    else:
        logger.info(f"El atributo TTL '{TTL_FIELD_NAME}' ya está presente en la tabla")

# Función para migrar datos a la tabla de respaldo
def migrate_data(backup_table_name):
    logger.info(f"Iniciando migración de datos a la tabla de respaldo: {backup_table_name}")

    # Obtener los ítems de la tabla original
    logger.info(f"Obteniendo ítems de la tabla original: {TABLE_NAME}")
    items = get_items(TABLE_NAME)
    logger.info(f"Total de ítems obtenidos: {len(items)}")

    if not items:
        logger.info(f"No hay datos para migrar a {backup_table_name}")
        return

    # Migrar datos uno por uno usando put_item
    for index, record in enumerate(items):
        logger.info(f"Iniciando migración del ítem {index + 1}/{len(items)}: {record}")

        # Handle missing keys with default values
        item = {
            'idPago': {'S': record.get('idPago', {}).get('S', '')},
            'UTCTimeFormat': {'S': record.get('UTCTimeFormat', {}).get('S', '')},
            'additionalInfo': {'S': record.get('additionalInfo', {}).get('S', '')},
            'attendant': {'S': record.get('attendant', {}).get('S', '')},
            'currencyCode': {'S': record.get('currencyCode', {}).get('S', '')},
            'datosComercio': {'M': {
                'MCC': {'S': record.get('datosComercio', {}).get('MCC', {}).get('S', '')},
                'ciudadComercio': {'S': record.get('datosComercio', {}).get('ciudadComercio', {}).get('S', '')},
                'clientAppOrg': {'S': record.get('datosComercio', {}).get('clientAppOrg', {}).get('S', '')},
                'comunaComercio': {'S': record.get('datosComercio', {}).get('comunaComercio', {}).get('S', '')},
                'dv': {'S': record.get('datosComercio', {}).get('dv', {}).get('S', '')},
                'idComercio': {'S': record.get('datosComercio', {}).get('idComercio', {}).get('S', '')},
                'paisComercio': {'S': record.get('datosComercio', {}).get('paisComercio', {}).get('S', '')},
                'rut': {'S': record.get('datosComercio', {}).get('rut', {}).get('S', '')}
            }},
            'datosPago': {'M': {
                'cuotas': {'N': str(record.get('datosPago', {}).get('cuotas', {}).get('N', '0'))},
                'iva': {'N': str(record.get('datosPago', {}).get('iva', {}).get('N', '0'))},
                'monto': {'N': str(record.get('datosPago', {}).get('monto', {}).get('N', '0'))}
            }},
            'fecha': {'S': record.get('fecha', {}).get('S', '')},
            TTL_FIELD_NAME: {'N': calculate_ttl()}
        }

        logger.info(f"item info: {record}")

        # Migrar el ítem a la tabla de respaldo
        try:
            dynamodb_client.put_item(TableName=backup_table_name, Item=item)
            logger.info(f"Ítem {index + 1}/{len(items)} migrado exitosamente")
        except ClientError as e:
            logger.error(f"Error al migrar el ítem {index + 1}/{len(items)}: {e.response['Error']['Message']}")
            raise

# Función principal para realizar la copia de seguridad
def run_backup():
    logger.info("Iniciando el proceso de copia de seguridad")
    try:
        backup_table_name = create_backup_table()
        migrate_data(backup_table_name)
        add_ttl_attribute(backup_table_name)
        logger.info(f"Copia de seguridad completada exitosamente en la tabla: {backup_table_name}")
    except Exception as e:
        logger.error(f"Error en el proceso de copia de seguridad: {str(e)}")

if __name__ == '__main__':
    run_backup()

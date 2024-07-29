import boto3
import os
import logging
from datetime import datetime
import time
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de DynamoDB desde las variables de entorno
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

        item = {
            'idPago': {'S': record['idPago']},
            'UTCTimeFormat': {'S': record['UTCTimeFormat']},
            'additionalInfo': {'S': record['additionalInfo']},
            'attendant': {'S': record['attendant']},
            'currencyCode': {'S': record['currencyCode']},
            'datosComercio': {'M': {
                'MCC': {'S': record['datosComercio']['MCC']},
                'ciudadComercio': {'S': record['datosComercio']['ciudadComercio']},
                'clientAppOrg': {'S': record['datosComercio']['clientAppOrg']},
                'comunaComercio': {'S': record['datosComercio']['comunaComercio']},
                'dv': {'S': record['datosComercio']['dv']},
                'idComercio': {'S': record['datosComercio']['idComercio']},
                'paisComercio': {'S': record['datosComercio']['paisComercio']},
                'rut': {'S': record['datosComercio']['rut']}
            }},
            'datosPago': {'M': {
                'cuotas': {'N': str(record['datosPago']['cuotas'])},
                'iva': {'N': str(record['datosPago']['iva'])},
                'monto': {'N': str(record['datosPago']['monto'])},
                'monto_s_prop': {'N': str(record['datosPago']['monto_s_prop'])},
                'neto': {'N': str(record['datosPago']['neto'])},
                'propina': {'N': str(record['datosPago']['propina'])},
                'tipoComprobante': {'S': record['datosPago']['tipoComprobante']},
                'tipoCuota': {'S': record['datosPago']['tipoCuota']},
                'totalExento': {'N': str(record['datosPago']['totalExento'])},
                'vuelto': {'N': str(record['datosPago']['vuelto'])}
            }},
            'datosSucursal': {'M': {
                'comunaSucursal': {'S': record['datosSucursal']['comunaSucursal']},
                'direccionSucursal': {'S': record['datosSucursal']['direccionSucursal']},
                'idSucursal': {'S': record['datosSucursal']['idSucursal']},
                'idSucursalOP': {'S': record['datosSucursal']['idSucursalOP']},
                'nombreSucursal': {'S': record['datosSucursal']['nombreSucursal']},
                'paisSucursal': {'S': record['datosSucursal']['paisSucursal']},
                'regionSucursal': {'S': record['datosSucursal']['regionSucursal']}
            }},
            'datosTarjeta': {'M': {
                'bin': {'S': record['datosTarjeta']['bin']},
                'abreviatura': {'S': record['datosTarjeta']['abreviatura']},
                'marca': {'S': record['datosTarjeta']['marca']},
                'cardEntryMode': {'S': record['datosTarjeta']['cardEntryMode']},
                'cardSeqNumb': {'S': record['datosTarjeta']['cardSeqNumb']},
                'tipo': {'S': record['datosTarjeta']['tipo']},
                'conditionCode': {'S': record['datosTarjeta']['conditionCode']},
                'fourDigits': {'S': record['datosTarjeta']['fourDigits']},
                'invoiceData': {'S': record['datosTarjeta']['invoiceData']}
            }},
            'idTerminal': {'S': record['idTerminal']},
            'infoAdicional': {'M': {
                'canal': {'S': record['infoAdicional']['canal']},
                'card_entry': {'S': record['infoAdicional']['card_entry']},
                'portador': {'S': record['infoAdicional']['portador']},
                'serial_number': {'S': record['infoAdicional']['serial_number']},
                'sim_id': {'S': record['infoAdicional']['sim_id']},
                'version_app': {'S': record['infoAdicional']['version_app']},
                'bins': {'M': {
                    'date_file': {'S': record['infoAdicional']['bins']['date_file']},
                    'date_update': {'S': record['infoAdicional']['bins']['date_update']},
                    'record_count': {'N': str(record['infoAdicional']['bins']['record_count'])},
                    'version': {'N': str(record['infoAdicional']['bins']['version'])}
                }},
                'emv_aid': {'M': {
                    'date_file': {'S': record['infoAdicional']['emv_aid']['date_file']},
                    'date_update': {'S': record['infoAdicional']['emv_aid']['date_update']},
                    'version': {'N': str(record['infoAdicional']['emv_aid']['version'])}
                }},
                'emv_capk': {'M': {
                    'date_file': {'S': record['infoAdicional']['emv_capk']['date_file']},
                    'date_update': {'S': record['infoAdicional']['emv_capk']['date_update']},
                    'version': {'N': str(record['infoAdicional']['emv_capk']['version'])}
                }},
                'errors': {'M': {
                    'date_file': {'S': record['infoAdicional']['errors']['date_file']},
                    'date_update': {'S': record['infoAdicional']['errors']['date_update']},
                    'version': {'N': str(record['infoAdicional']['errors']['version'])}
                }},
                'propinaActiva': {'BOOL': record['infoAdicional']['propinaActiva']}
            }},
            'localDate': {'S': record['localDate']},
            'localTime': {'S': record['localTime']},
            'localTimeFormat': {'S': record['localTimeFormat']},
            'millisecDate': {'S': record['millisecDate']},
            'ocAlianza': {'S': record['ocAlianza']},
            'rrn': {'S': record['rrn']}
        }

        # Add the TTL attribute to each item
        item[TTL_FIELD_NAME] = {'N': str(calculate_ttl())}

        # Log the item information after adding the TTL
        logger.debug(f"Item con TTL añadido {index + 1}/{len(items)}: {item}")

        # Try to put the item into the table
        try:
            dynamodb_client.put_item(TableName=backup_table_name, Item=item)
            logger.info(f"Ítem {index + 1}/{len(items)} migrado exitosamente")
        except ClientError as e:
            logger.error(f"Error al migrar el ítem {index + 1}/{len(items)}: {e}")
            logger.error(f"Detalles del ítem que causó el error: {item}")
        except Exception as e:
            logger.error(f"Error inesperado al migrar el ítem {index + 1}/{len(items)}: {e}")
            logger.error(f"Detalles del ítem que causó el error: {item}")

    logger.info(f"Datos migrados a {backup_table_name} con éxito")

# Función para eliminar la tabla original
def delete_table():
    dynamodb_client.delete_table(TableName=TABLE_NAME)
    logger.info(f"Tabla {TABLE_NAME} eliminada")

# Función para habilitar TTL en la nueva tabla
def enable_ttl(backup_table_name):
    dynamodb_client.update_time_to_live(
        TableName=backup_table_name,
        TimeToLiveSpecification={
            'Enabled': True,
            'AttributeName': TTL_FIELD_NAME
        }
    )

    logger.info(f"TTL habilitado en la tabla {backup_table_name}")

# Ejecutar el flujo de trabajo
def main():
    backup_table_name = create_backup_table()
    migrate_data(backup_table_name)
    add_ttl_attribute(backup_table_name)
    enable_ttl(backup_table_name)

if __name__ == '__main__':
    main()

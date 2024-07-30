import boto3
import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
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

# Función para mostrasr string fecha a partir de un timestamp
def timestamp_to_string(timestamp):
    """
    Convierte un timestamp a una fecha en formato 'YYYY-MM-DD HH:MM:SS'.
    
    :param timestamp: El timestamp a convertir (en segundos).
    :return: Fecha en formato de cadena 'YYYY-MM-DD HH:MM:SS'.
    """
    # Convierte el timestamp a un objeto datetime
    dt_object = datetime.fromtimestamp(timestamp)
    
    # Formatea el objeto datetime como una cadena
    date_string = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    
    return date_string

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

        calculate_ttl_value = calculate_ttl()
        calculate_ttl_value_formatter = timestamp_to_string(calculate_ttl_value)

        # Handle missing keys with default values
        item = {
            'idPago': {'S': record['idPago']},
            'attendant': {'S': record['attendant']},
            'codigoAutorizacion': {'S': record.get('codigoAutorizacion', '')},
            'datosComercio': {'M': {
                'ciudadComercio': {'S': record['datosComercio']['ciudadComercio']},
                'clientAppOrg': {'S': record['datosComercio']['clientAppOrg']},
                'comunaComercio': {'S': record['datosComercio']['comunaComercio']},
                'dv': {'S': record['datosComercio']['dv']},
                'idComercio': {'S': record['datosComercio']['idComercio']},
                'MCC': {'S': record['datosComercio']['MCC']},
                'paisComercio': {'S': record['datosComercio']['paisComercio']},
                'rut': {'S': record['datosComercio']['rut']}
            }},
            'datosPago': {'M': {
                'cuotas': {'S': record['datosPago']['cuotas']},
                'iva': {'N': str(record['datosPago']['iva'])},
                'monto': {'N': str(record['datosPago']['monto'])},
                'neto': {'N': str(record['datosPago']['neto'])},
                'propina': {'N': str(record['datosPago']['propina'])},
                'tipoComprobante': {'S': record['datosPago']['tipoComprobante']},
                'tipoCuota': {'S': record['datosPago']['tipoCuota']},
                'totalExento': {'N': str(record['datosPago']['totalExento'])}
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
                'abreviatura': {'S': record['datosTarjeta']['abreviatura']},
                'bin': {'S': record['datosTarjeta']['bin']},
                'cardEntryMode': {'S': record['datosTarjeta']['cardEntryMode']},
                'cardSeqNumb': {'S': record['datosTarjeta']['cardSeqNumb']},
                'conditionCode': {'S': record['datosTarjeta']['conditionCode']},
                'fourDigits': {'S': record['datosTarjeta']['fourDigits']},
                'invoiceData': {'S': record['datosTarjeta']['invoiceData']},
                'marca': {'S': record['datosTarjeta']['marca']},
                'tipo': {'S': record['datosTarjeta']['tipo']}
            }},
            'diaNumSerie': {'S': record.get('diaNumSerie', '')},
            'diaNumSerieEstado': {'S': record.get('diaNumSerieEstado', '')},
            'estado': {'S': record['estado']},
            'fecha': {'S': record['fecha']},
            'fechaAnulacion': {'NULL': True} if record['fechaAnulacion'] is None else {'S': record['fechaAnulacion']},
            'fechaDia': {'S': record['fechaDia']},
            'fechaUTC': {'S': record['fechaUTC']},
            'idComercio': {'S': record['idComercio']},
            'idTerminal': {'S': record['idTerminal']},
            'infoAdicionalPOS': {'M': {
                'bins': {'M': {
                    'date_file': {'S': record['infoAdicionalPOS']['bins']['date_file']},
                    'date_update': {'S': record['infoAdicionalPOS']['bins']['date_update']},
                    'record_count': {'N': str(record['infoAdicionalPOS']['bins']['record_count'])},
                    'version': {'N': str(record['infoAdicionalPOS']['bins']['version'])}
                }},
                'canal': {'S': record['infoAdicionalPOS']['canal']},
                'card_entry': {'S': record['infoAdicionalPOS']['card_entry']},
                'emv_aid': {'M': {
                    'date_file': {'S': record['infoAdicionalPOS']['emv_aid']['date_file']},
                    'date_update': {'S': record['infoAdicionalPOS']['emv_aid']['date_update']},
                    'version': {'N': str(record['infoAdicionalPOS']['emv_aid']['version'])}
                }},
                'emv_capk': {'M': {
                    'date_file': {'S': record['infoAdicionalPOS']['emv_capk']['date_file']},
                    'date_update': {'S': record['infoAdicionalPOS']['emv_capk']['date_update']},
                    'version': {'N': str(record['infoAdicionalPOS']['emv_capk']['version'])}
                }},
                'errors': {'M': {
                    'date_file': {'S': record['infoAdicionalPOS']['errors']['date_file']},
                    'date_update': {'S': record['infoAdicionalPOS']['errors']['date_update']},
                    'version': {'N': str(record['infoAdicionalPOS']['errors']['version'])}
                }},
                'portador': {'S': record['infoAdicionalPOS']['portador']},
                'propinaActiva': {'BOOL': record['infoAdicionalPOS']['propinaActiva']},
                'serial_number': {'S': record['infoAdicionalPOS']['serial_number']},
                'sim_id': {'S': record['infoAdicionalPOS']['sim_id']},
                'version_app': {'S': record['infoAdicionalPOS']['version_app']}
            }},
            'log': {'L': [
                {'M': {
                    'idPago': {'S': log_entry['idPago']},
                    'estado': {'S': log_entry['estado']},
                    'fechas': {'M': {
                        'fechaAnulacion': {'NULL': True} if log_entry['fechas']['fechaAnulacion'] is None else {'S': log_entry['fechas']['fechaAnulacion']},
                        'fechaAPILocal': {'S': log_entry['fechas']['fechaAPILocal']},
                        'fechaAPIUTC': {'S': log_entry['fechas']['fechaAPIUTC']},
                        'fechaPOSLocal': {'S': log_entry['fechas']['fechaPOSLocal']},
                        'fechaPOSUTC': {'S': log_entry['fechas']['fechaPOSUTC']}
                    }},
                    'infoAdicionalPOS': {'M': {
                        'bins': {'M': {
                            'date_file': {'S': log_entry['infoAdicionalPOS']['bins']['date_file']},
                            'date_update': {'S': log_entry['infoAdicionalPOS']['bins']['date_update']},
                            'record_count': {'N': str(log_entry['infoAdicionalPOS']['bins']['record_count'])},
                            'version': {'N': str(log_entry['infoAdicionalPOS']['bins']['version'])}
                        }},
                        'canal': {'S': log_entry['infoAdicionalPOS']['canal']},
                        'card_entry': {'S': log_entry['infoAdicionalPOS']['card_entry']},
                        'emv_aid': {'M': {
                            'date_file': {'S': log_entry['infoAdicionalPOS']['emv_aid']['date_file']},
                            'date_update': {'S': log_entry['infoAdicionalPOS']['emv_aid']['date_update']},
                            'version': {'N': str(log_entry['infoAdicionalPOS']['emv_aid']['version'])}
                        }},
                        'emv_capk': {'M': {
                            'date_file': {'S': log_entry['infoAdicionalPOS']['emv_capk']['date_file']},
                            'date_update': {'S': log_entry['infoAdicionalPOS']['emv_capk']['date_update']},
                            'version': {'N': str(log_entry['infoAdicionalPOS']['emv_capk']['version'])}
                        }},
                        'errors': {'M': {
                            'date_file': {'S': log_entry['infoAdicionalPOS']['errors']['date_file']},
                            'date_update': {'S': log_entry['infoAdicionalPOS']['errors']['date_update']},
                            'version': {'N': str(log_entry['infoAdicionalPOS']['errors']['version'])}
                        }},
                        'portador': {'S': log_entry['infoAdicionalPOS']['portador']},
                        'propinaActiva': {'BOOL': log_entry['infoAdicionalPOS']['propinaActiva']},
                        'serial_number': {'S': log_entry['infoAdicionalPOS']['serial_number']},
                        'sim_id': {'S': log_entry['infoAdicionalPOS']['sim_id']},
                        'version_app': {'S': log_entry['infoAdicionalPOS']['version_app']}
                    }}
                }} for log_entry in record['log']
            ]}
        }

        logger.info(f"ttl calculado: {calculate_ttl_value}")
        logger.info(f"ttl formateado: {calculate_ttl_value_formatter}")
        logger.info(f"item {index + 1} info: {record}")
        
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

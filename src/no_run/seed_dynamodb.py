import json
import boto3
import os
import logging
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Para mostrar los logs en la consola
        logging.FileHandler('dynamodb_operations.log')  # Para almacenar los logs en un archivo
    ]
)
logger = logging.getLogger()

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de DynamoDB desde las variables de entorno
DYNAMODB_PORT = os.getenv('DYNAMODB_PORT', 8000)
DYNAMODB_HOST = os.getenv('DYNAMODB_HOST', 'localhost')
DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT', 'http://dynamodb-local:8000')

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'fakemykeyid')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'fakemysecretaccesskey')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# DB
TABLE_NAME = os.getenv('TABLE_BE_AD_API_POS_PAGOS', 'be-ad-api-pos-pagos')
TABLE_DATA_JSON_SOURCE_PATH = 'no_run/db_pago.json'

logger.info(f"DYNAMODB_PORT '{DYNAMODB_PORT}'.")
logger.info(f"DYNAMODB_HOST '{DYNAMODB_HOST}'.")
logger.info(f"DYNAMODB_ENDPOINT '{DYNAMODB_ENDPOINT}'.")
logger.info(f"AWS_ACCESS_KEY_ID '{AWS_ACCESS_KEY_ID}'.")
logger.info(f"AWS_SECRET_ACCESS_KEY '{AWS_SECRET_ACCESS_KEY}'.")
logger.info(f"AWS_REGION '{AWS_REGION}'.")
logger.info(f"TABLE_NAME '{TABLE_NAME}'.")

# Nombre de la tabla DynamoDB

def create_dynamodb_client():
    """Crea un cliente de DynamoDB usando la configuración local."""
    try:
        return boto3.client(
            'dynamodb',
            endpoint_url=DYNAMODB_ENDPOINT,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"Error de credenciales: {e}")
        raise

def create_table(dynamodb_client):
    """Crea una tabla en DynamoDB si no existe."""
    try:
        # Verificar si la tabla ya existe
        tables = dynamodb_client.list_tables()
        if TABLE_NAME in tables.get('TableNames', []):
            logger.info(f"La tabla '{TABLE_NAME}' ya existe.")
            return
        
        # Crear la tabla si no existe
        dynamodb_client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'idPago', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'idPago', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        logger.info(f"Tabla '{TABLE_NAME}' creada con éxito.")
    except Exception as e:
        logger.error(f"Error al crear la tabla '{TABLE_NAME}': {e}")
        raise

def load_json_file(file_path):
    """Carga datos desde un archivo JSON."""
    with open(file_path, 'r') as file:
        return json.load(file)

def insert_data_to_dynamodb(dynamodb_client, table_name, data):
    """Inserta datos en una tabla DynamoDB."""
    for record in data:
        try:
            dynamodb_client.put_item(
                TableName=table_name,
                Item={
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
            )
            logger.info(f"Registro insertado exitosamente: {record['idPago']}")
        except Exception as e:
            logger.error(f"Error al insertar el registro con idPago '{record['idPago']}': {e}")

def main():
    file_path = TABLE_DATA_JSON_SOURCE_PATH
    dynamodb_client = create_dynamodb_client()
    create_table(dynamodb_client)
    data = load_json_file(file_path)
    insert_data_to_dynamodb(dynamodb_client, TABLE_NAME, data)

if __name__ == '__main__':
    main()

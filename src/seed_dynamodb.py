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

# Table Name
TABLE_NAME = os.getenv('TABLE_BE_AD_API_POS_PAGOS', 'be-ad-api-pos-pagos')

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
            )
            logger.info(f"Registro insertado exitosamente: {record['idPago']}")
        except Exception as e:
            logger.error(f"Error al insertar el registro con idPago '{record['idPago']}': {e}")

def main():
    file_path = 'db_pago.json'
    dynamodb_client = create_dynamodb_client()
    create_table(dynamodb_client)
    data = load_json_file(file_path)
    insert_data_to_dynamodb(dynamodb_client, TABLE_NAME, data)

if __name__ == '__main__':
    main()

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de variables de entorno
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'fakemykeyid')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'fakemysecretaccesskey')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', 'fakemysessiontoken')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Inicializa el cliente de Kinesis
kinesis_client = boto3.client(
    'kinesis',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para crear un stream en Kinesis
def create_kinesis_stream(stream_name, shard_count=1):
    try:
        response = kinesis_client.create_stream(StreamName=stream_name, ShardCount=shard_count)
        return response
    except ClientError as e:
        print(f"Error al crear el stream {stream_name}: {e.response['Error']['Message']}")
        return None

# Método para poner un registro en un stream de Kinesis
def put_record(stream_name, data, partition_key):
    try:
        response = kinesis_client.put_record(StreamName=stream_name, Data=data, PartitionKey=partition_key)
        return response
    except ClientError as e:
        print(f"Error al poner el registro en el stream {stream_name}: {e.response['Error']['Message']}")
        return None

# Método para obtener registros de un stream de Kinesis
def get_records(stream_name, shard_id, shard_iterator_type='LATEST', limit=10):
    try:
        # Obtener el shard iterator
        response = kinesis_client.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard_id,
            ShardIteratorType=shard_iterator_type
        )
        shard_iterator = response['ShardIterator']
        
        # Obtener registros
        response = kinesis_client.get_records(ShardIterator=shard_iterator, Limit=limit)
        return response['Records']
    except ClientError as e:
        print(f"Error al obtener los registros del stream {stream_name}: {e.response['Error']['Message']}")
        return None

# Método para describir un stream de Kinesis
def describe_stream(stream_name):
    try:
        response = kinesis_client.describe_stream(StreamName=stream_name)
        return response['StreamDescription']
    except ClientError as e:
        print(f"Error al describir el stream {stream_name}: {e.response['Error']['Message']}")
        return None

# Método para eliminar un stream de Kinesis
def delete_kinesis_stream(stream_name):
    try:
        response = kinesis_client.delete_stream(StreamName=stream_name)
        return response
    except ClientError as e:
        print(f"Error al eliminar el stream {stream_name}: {e.response['Error']['Message']}")
        return None

# Método para listar los streams de Kinesis
def list_kinesis_streams():
    try:
        response = kinesis_client.list_streams()
        return response['StreamNames']
    except ClientError as e:
        print(f"Error al listar los streams de Kinesis: {e.response['Error']['Message']}")
        return []

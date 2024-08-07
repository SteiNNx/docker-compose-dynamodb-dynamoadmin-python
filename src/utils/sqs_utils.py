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

# Inicializa el cliente de SQS
sqs_client = boto3.client(
    'sqs',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para crear una cola SQS
def create_queue(queue_name):
    try:
        response = sqs_client.create_queue(QueueName=queue_name)
        return response['QueueUrl']
    except ClientError as e:
        print(f"Error al crear la cola {queue_name}: {e.response['Error']['Message']}")
        return None

# Método para enviar un mensaje a una cola SQS
def send_message(queue_url, message_body):
    try:
        response = sqs_client.send_message(QueueUrl=queue_url, MessageBody=message_body)
        return response
    except ClientError as e:
        print(f"Error al enviar mensaje a la cola {queue_url}: {e.response['Error']['Message']}")
        return None

# Método para recibir un mensaje de una cola SQS
def receive_message(queue_url):
    try:
        response = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        return response.get('Messages', [])
    except ClientError as e:
        print(f"Error al recibir mensaje de la cola {queue_url}: {e.response['Error']['Message']}")
        return []

# Método para eliminar un mensaje de una cola SQS
def delete_message(queue_url, receipt_handle):
    try:
        response = sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        return response
    except ClientError as e:
        print(f"Error al eliminar mensaje de la cola {queue_url}: {e.response['Error']['Message']}")
        return None

# Método para listar todas las colas SQS
def list_queues():
    try:
        response = sqs_client.list_queues()
        return response.get('QueueUrls', [])
    except ClientError as e:
        print(f"Error al listar colas SQS: {e.response['Error']['Message']}")
        return []

# Método para obtener la URL de una cola SQS por nombre
def get_queue_url(queue_name):
    try:
        response = sqs_client.get_queue_url(QueueName=queue_name)
        return response['QueueUrl']
    except ClientError as e:
        print(f"Error al obtener la URL de la cola {queue_name}: {e.response['Error']['Message']}")
        return None

# Método para eliminar una cola SQS
def delete_queue(queue_url):
    try:
        response = sqs_client.delete_queue(QueueUrl=queue_url)
        return response
    except ClientError as e:
        print(f"Error al eliminar la cola {queue_url}: {e.response['Error']['Message']}")
        return None

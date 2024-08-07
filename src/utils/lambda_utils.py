import boto3
import json
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

# Inicializa el cliente de Lambda
lambda_client = boto3.client(
    'lambda',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para crear una función Lambda
def create_lambda_function(function_name, role_arn, handler, zip_file):
    try:
        with open(zip_file, 'rb') as f:
            zipped_code = f.read()
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.8',
            Role=role_arn,
            Handler=handler,
            Code=dict(ZipFile=zipped_code),
            Timeout=300
        )
        return response
    except ClientError as e:
        print(f"Error al crear la función Lambda {function_name}: {e.response['Error']['Message']}")
        return None

# Método para actualizar el código de una función Lambda
def update_lambda_function_code(function_name, zip_file):
    try:
        with open(zip_file, 'rb') as f:
            zipped_code = f.read()
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zipped_code
        )
        return response
    except ClientError as e:
        print(f"Error al actualizar el código de la función Lambda {function_name}: {e.response['Error']['Message']}")
        return None

# Método para invocar una función Lambda
def invoke_lambda_function(function_name, payload):
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        return json.load(response['Payload'])
    except ClientError as e:
        print(f"Error al invocar la función Lambda {function_name}: {e.response['Error']['Message']}")
        return None

# Método para obtener información sobre una función Lambda
def get_lambda_function_info(function_name):
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        return response
    except ClientError as e:
        print(f"Error al obtener información de la función Lambda {function_name}: {e.response['Error']['Message']}")
        return None

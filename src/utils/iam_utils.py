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

# Inicializa el cliente de IAM
iam_client = boto3.client(
    'iam',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para crear un usuario IAM
def create_user(user_name):
    try:
        response = iam_client.create_user(UserName=user_name)
        return response
    except ClientError as e:
        print(f"Error al crear el usuario IAM {user_name}: {e.response['Error']['Message']}")
        return None

# Método para eliminar un usuario IAM
def delete_user(user_name):
    try:
        response = iam_client.delete_user(UserName=user_name)
        return response
    except ClientError as e:
        print(f"Error al eliminar el usuario IAM {user_name}: {e.response['Error']['Message']}")
        return None

# Método para adjuntar una política a un usuario IAM
def attach_user_policy(user_name, policy_arn):
    try:
        response = iam_client.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)
        return response
    except ClientError as e:
        print(f"Error al adjuntar la política {policy_arn} al usuario IAM {user_name}: {e.response['Error']['Message']}")
        return None

# Método para desadjuntar una política de un usuario IAM
def detach_user_policy(user_name, policy_arn):
    try:
        response = iam_client.detach_user_policy(UserName=user_name, PolicyArn=policy_arn)
        return response
    except ClientError as e:
        print(f"Error al desadjuntar la política {policy_arn} del usuario IAM {user_name}: {e.response['Error']['Message']}")
        return None

# Método para listar todos los usuarios IAM
def list_users():
    try:
        response = iam_client.list_users()
        return response['Users']
    except ClientError as e:
        print(f"Error al listar los usuarios IAM: {e.response['Error']['Message']}")
        return []

# Método para describir un usuario IAM
def describe_user(user_name):
    try:
        response = iam_client.get_user(UserName=user_name)
        return response['User']
    except ClientError as e:
        print(f"Error al describir el usuario IAM {user_name}: {e.response['Error']['Message']}")
        return None

# Método para listar las políticas adjuntas a un usuario IAM
def list_attached_user_policies(user_name):
    try:
        response = iam_client.list_attached_user_policies(UserName=user_name)
        return response['AttachedPolicies']
    except ClientError as e:
        print(f"Error al listar las políticas adjuntas del usuario IAM {user_name}: {e.response['Error']['Message']}")
        return []

# Método para listar las políticas de usuario IAM no adjuntas
def list_available_policies():
    try:
        response = iam_client.list_policies(Scope='Local')  # 'Local' para políticas de usuario, 'All' para todas las políticas
        return response['Policies']
    except ClientError as e:
        print(f"Error al listar las políticas disponibles: {e.response['Error']['Message']}")
        return []

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

def handle_client_error(error, action, resource_name):
    """
    Maneja los errores del cliente y muestra mensajes informativos.

    Parámetros:
    - error (ClientError): El objeto de excepción que contiene los detalles del error.
    - action (str): La acción que se estaba realizando cuando ocurrió el error.
    - resource_name (str): El nombre del recurso involucrado en el error.
    """
    print(f"Error al {action} {resource_name}: {error.response['Error']['Message']}")

def create_user(user_name):
    """
    Crea un nuevo usuario IAM.

    Parámetros:
    - user_name (str): El nombre del usuario IAM a crear.

    Retorna:
    - dict: La respuesta del cliente de IAM en caso de éxito.
    - None: Si ocurre un error durante la creación del usuario.
    """
    try:
        response = iam_client.create_user(UserName=user_name)
        return response
    except ClientError as e:
        handle_client_error(e, "crear el usuario IAM", user_name)
        return None

def delete_user(user_name):
    """
    Elimina un usuario IAM existente.

    Parámetros:
    - user_name (str): El nombre del usuario IAM a eliminar.

    Retorna:
    - dict: La respuesta del cliente de IAM en caso de éxito.
    - None: Si ocurre un error durante la eliminación del usuario.
    """
    try:
        response = iam_client.delete_user(UserName=user_name)
        return response
    except ClientError as e:
        handle_client_error(e, "eliminar el usuario IAM", user_name)
        return None

def attach_user_policy(user_name, policy_arn):
    """
    Adjunta una política a un usuario IAM.

    Parámetros:
    - user_name (str): El nombre del usuario IAM al que se le adjuntará la política.
    - policy_arn (str): El ARN de la política que se adjuntará al usuario.

    Retorna:
    - dict: La respuesta del cliente de IAM en caso de éxito.
    - None: Si ocurre un error durante la adjunción de la política.
    """
    try:
        response = iam_client.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)
        return response
    except ClientError as e:
        handle_client_error(e, "adjuntar la política", f"{policy_arn} al usuario IAM {user_name}")
        return None

def detach_user_policy(user_name, policy_arn):
    """
    Desadjunta una política de un usuario IAM.

    Parámetros:
    - user_name (str): El nombre del usuario IAM del que se desadjuntará la política.
    - policy_arn (str): El ARN de la política que se desadjuntará del usuario.

    Retorna:
    - dict: La respuesta del cliente de IAM en caso de éxito.
    - None: Si ocurre un error durante la desadjunción de la política.
    """
    try:
        response = iam_client.detach_user_policy(UserName=user_name, PolicyArn=policy_arn)
        return response
    except ClientError as e:
        handle_client_error(e, "desadjuntar la política", f"{policy_arn} del usuario IAM {user_name}")
        return None

def list_users():
    """
    Lista todos los usuarios IAM existentes.

    Retorna:
    - list: Una lista de diccionarios que contienen la información de cada usuario IAM.
    - list: Una lista vacía si ocurre un error al listar los usuarios.
    """
    try:
        response = iam_client.list_users()
        return response['Users']
    except ClientError as e:
        handle_client_error(e, "listar los usuarios IAM", "")
        return []

def describe_user(user_name):
    """
    Describe un usuario IAM específico.

    Parámetros:
    - user_name (str): El nombre del usuario IAM a describir.

    Retorna:
    - dict: Un diccionario con la información del usuario IAM.
    - None: Si ocurre un error durante la descripción del usuario.
    """
    try:
        response = iam_client.get_user(UserName=user_name)
        return response['User']
    except ClientError as e:
        handle_client_error(e, "describir el usuario IAM", user_name)
        return None

def list_attached_user_policies(user_name):
    """
    Lista las políticas adjuntas a un usuario IAM específico.

    Parámetros:
    - user_name (str): El nombre del usuario IAM cuyas políticas adjuntas se listarán.

    Retorna:
    - list: Una lista de diccionarios que contienen las políticas adjuntas al usuario.
    - list: Una lista vacía si ocurre un error al listar las políticas.
    """
    try:
        response = iam_client.list_attached_user_policies(UserName=user_name)
        return response['AttachedPolicies']
    except ClientError as e:
        handle_client_error(e, "listar las políticas adjuntas del usuario IAM", user_name)
        return []

def list_available_policies():
    """
    Lista las políticas de usuario IAM disponibles.

    Retorna:
    - list: Una lista de diccionarios que contienen las políticas disponibles.
    - list: Una lista vacía si ocurre un error al listar las políticas.
    """
    try:
        response = iam_client.list_policies(Scope='Local')  # 'Local' para políticas de usuario, 'All' para todas las políticas
        return response['Policies']
    except ClientError as e:
        handle_client_error(e, "listar las políticas disponibles", "")
        return []

def main():
    """
    Función principal para ejecutar ejemplos de uso de las funciones definidas.
    """
    # Ejemplo de creación de usuario
    user_name = 'example-user'
    print(f"Creando usuario IAM '{user_name}'...")
    create_user_response = create_user(user_name)
    if create_user_response:
        print(f"Usuario '{user_name}' creado exitosamente: {create_user_response}")

    # Ejemplo de listar usuarios
    print("Listando usuarios IAM...")
    users = list_users()
    print(f"Usuarios IAM: {users}")

    # Ejemplo de describir usuario
    print(f"Describiendo usuario IAM '{user_name}'...")
    user_description = describe_user(user_name)
    print(f"Descripción del usuario '{user_name}': {user_description}")

    # Ejemplo de eliminar usuario
    print(f"Eliminando usuario IAM '{user_name}'...")
    delete_user_response = delete_user(user_name)
    if delete_user_response:
        print(f"Usuario '{user_name}' eliminado exitosamente")

if __name__ == "__main__":
    main()

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

# Inicializa el cliente de CloudFormation
cloudformation_client = boto3.client(
    'cloudformation',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

def create_stack(stack_name, template_body, parameters=None):
    """
    Crea un stack en AWS CloudFormation.
    :param stack_name: Nombre del stack a crear.
    :param template_body: Plantilla en formato JSON o YAML para el stack.
    :param parameters: Parámetros opcionales para el stack.
    :return: Respuesta de la creación del stack.
    """
    try:
        response = cloudformation_client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters or []
        )
        return response
    except ClientError as e:
        print(f"Error al crear el stack {stack_name}: {e.response['Error']['Message']}")
        return None

def update_stack(stack_name, template_body, parameters=None):
    """
    Actualiza un stack en AWS CloudFormation.
    :param stack_name: Nombre del stack a actualizar.
    :param template_body: Plantilla en formato JSON o YAML para el stack.
    :param parameters: Parámetros opcionales para el stack.
    :return: Respuesta de la actualización del stack.
    """
    try:
        response = cloudformation_client.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters or []
        )
        return response
    except ClientError as e:
        print(f"Error al actualizar el stack {stack_name}: {e.response['Error']['Message']}")
        return None

def delete_stack(stack_name):
    """
    Elimina un stack en AWS CloudFormation.
    :param stack_name: Nombre del stack a eliminar.
    :return: Respuesta de la eliminación del stack.
    """
    try:
        response = cloudformation_client.delete_stack(StackName=stack_name)
        return response
    except ClientError as e:
        print(f"Error al eliminar el stack {stack_name}: {e.response['Error']['Message']}")
        return None

def describe_stack(stack_name):
    """
    Describe un stack en AWS CloudFormation.
    :param stack_name: Nombre del stack a describir.
    :return: Detalles del stack.
    """
    try:
        response = cloudformation_client.describe_stacks(StackName=stack_name)
        return response['Stacks'][0] if 'Stacks' in response else None
    except ClientError as e:
        print(f"Error al describir el stack {stack_name}: {e.response['Error']['Message']}")
        return None

def list_stacks():
    """
    Lista todos los stacks en AWS CloudFormation.
    :return: Lista de resúmenes de stacks.
    """
    try:
        response = cloudformation_client.list_stacks()
        return response['StackSummaries']
    except ClientError as e:
        print(f"Error al listar los stacks: {e.response['Error']['Message']}")
        return []

def describe_stack_events(stack_name):
    """
    Obtiene los eventos de un stack en AWS CloudFormation.
    :param stack_name: Nombre del stack cuyos eventos se desean obtener.
    :return: Lista de eventos del stack.
    """
    try:
        response = cloudformation_client.describe_stack_events(StackName=stack_name)
        return response['StackEvents']
    except ClientError as e:
        print(f"Error al describir eventos del stack {stack_name}: {e.response['Error']['Message']}")
        return []

def get_template(stack_name):
    """
    Obtiene la plantilla de un stack en AWS CloudFormation.
    :param stack_name: Nombre del stack cuya plantilla se desea obtener.
    :return: Plantilla del stack.
    """
    try:
        response = cloudformation_client.get_template(StackName=stack_name)
        return response['TemplateBody']
    except ClientError as e:
        print(f"Error al obtener la plantilla del stack {stack_name}: {e.response['Error']['Message']}")
        return None

def stack_exists(stack_name):
    """
    Verifica si un stack existe en AWS CloudFormation.
    :param stack_name: Nombre del stack a verificar.
    :return: True si el stack existe, False si no existe.
    """
    try:
        response = cloudformation_client.describe_stacks(StackName=stack_name)
        return 'Stacks' in response and len(response['Stacks']) > 0
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError' and 'does not exist' in e.response['Error']['Message']:
            return False
        print(f"Error al verificar la existencia del stack {stack_name}: {e.response['Error']['Message']}")
        return False

def main():
    """
    Método principal que llama a cada una de las funciones para demostrar su uso.
    """
    # Define los parámetros que se usarán en las funciones
    stack_name = 'your-stack-name'
    template_body = """
    {
      "AWSTemplateFormatVersion": "2010-09-09",
      "Resources": {
        "S3Bucket": {
          "Type": "AWS::S3::Bucket"
        }
      }
    }
    """
    parameters = [
        {
            'ParameterKey': 'InstanceType',
            'ParameterValue': 't2.micro'
        }
    ]

    ### Crear un stack
    print("Creando el stack...")
    response = create_stack(stack_name, template_body, parameters)
    print("Respuesta de la creación del stack:", response)

    ### Actualizar un stack
    print("Actualizando el stack...")
    response = update_stack(stack_name, template_body, parameters)
    print("Respuesta de la actualización del stack:", response)

    ### Describir un stack
    print("Describiendo el stack...")
    stack_description = describe_stack(stack_name)
    print("Descripción del stack:", stack_description)

    ### Listar todos los stacks
    print("Listando todos los stacks...")
    stacks = list_stacks()
    print("Stacks encontrados:", stacks)

    ### Obtener eventos del stack
    print("Obteniendo eventos del stack...")
    stack_events = describe_stack_events(stack_name)
    print("Eventos del stack:", stack_events)

    ### Obtener la plantilla del stack
    print("Obteniendo la plantilla del stack...")
    template = get_template(stack_name)
    print("Plantilla del stack:", template)

    ### Verificar existencia del stack
    print("Verificando si el stack existe...")
    exists = stack_exists(stack_name)
    print(f"El stack {stack_name} {'existe' if exists else 'no existe'}.")

    ### Eliminar un stack
    print("Eliminando el stack...")
    response = delete_stack(stack_name)
    print("Respuesta de la eliminación del stack:", response)

# Ejecutar la función main si este archivo se ejecuta directamente
if __name__ == "__main__":
    main()

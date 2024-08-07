import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de variables de entorno para AWS
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'fakemykeyid')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'fakemysecretaccesskey')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', 'fakemysessiontoken')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Inicializa el cliente de EC2
ec2_client = boto3.client(
    'ec2',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

def start_instance(instance_id):
    """
    Inicia una instancia EC2.

    :param instance_id: ID de la instancia que se va a iniciar.
    :return: Respuesta del servicio EC2 si la operación es exitosa, None en caso de error.
    """
    try:
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        return response
    except ClientError as e:
        print(f"Error al iniciar la instancia {instance_id}: {e.response['Error']['Message']}")
        return None

def stop_instance(instance_id):
    """
    Detiene una instancia EC2.

    :param instance_id: ID de la instancia que se va a detener.
    :return: Respuesta del servicio EC2 si la operación es exitosa, None en caso de error.
    """
    try:
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        return response
    except ClientError as e:
        print(f"Error al detener la instancia {instance_id}: {e.response['Error']['Message']}")
        return None

def reboot_instance(instance_id):
    """
    Reinicia una instancia EC2.

    :param instance_id: ID de la instancia que se va a reiniciar.
    :return: Respuesta del servicio EC2 si la operación es exitosa, None en caso de error.
    """
    try:
        response = ec2_client.reboot_instances(InstanceIds=[instance_id])
        return response
    except ClientError as e:
        print(f"Error al reiniciar la instancia {instance_id}: {e.response['Error']['Message']}")
        return None

def describe_instance(instance_id):
    """
    Describe una instancia EC2.

    :param instance_id: ID de la instancia que se va a describir.
    :return: Detalles de la instancia si la operación es exitosa, None en caso de error.
    """
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        return response['Reservations'][0]['Instances'][0] if 'Reservations' in response and len(response['Reservations']) > 0 else None
    except ClientError as e:
        print(f"Error al describir la instancia {instance_id}: {e.response['Error']['Message']}")
        return None

def create_security_group(group_name, description, vpc_id):
    """
    Crea un grupo de seguridad en EC2.

    :param group_name: Nombre del grupo de seguridad.
    :param description: Descripción del grupo de seguridad.
    :param vpc_id: ID del VPC donde se creará el grupo de seguridad.
    :return: ID del grupo de seguridad si la operación es exitosa, None en caso de error.
    """
    try:
        response = ec2_client.create_security_group(GroupName=group_name, Description=description, VpcId=vpc_id)
        return response['GroupId']
    except ClientError as e:
        print(f"Error al crear el grupo de seguridad {group_name}: {e.response['Error']['Message']}")
        return None

def describe_security_group(group_id):
    """
    Describe un grupo de seguridad en EC2.

    :param group_id: ID del grupo de seguridad que se va a describir.
    :return: Detalles del grupo de seguridad si la operación es exitosa, None en caso de error.
    """
    try:
        response = ec2_client.describe_security_groups(GroupIds=[group_id])
        return response['SecurityGroups'][0] if 'SecurityGroups' in response and len(response['SecurityGroups']) > 0 else None
    except ClientError as e:
        print(f"Error al describir el grupo de seguridad {group_id}: {e.response['Error']['Message']}")
        return None

def delete_security_group(group_id):
    """
    Elimina un grupo de seguridad en EC2.

    :param group_id: ID del grupo de seguridad que se va a eliminar.
    :return: Respuesta del servicio EC2 si la operación es exitosa, None en caso de error.
    """
    try:
        response = ec2_client.delete_security_group(GroupId=group_id)
        return response
    except ClientError as e:
        print(f"Error al eliminar el grupo de seguridad {group_id}: {e.response['Error']['Message']}")
        return None

def list_instances():
    """
    Lista todas las instancias EC2.

    :return: Lista de instancias si la operación es exitosa, lista vacía en caso de error.
    """
    try:
        response = ec2_client.describe_instances()
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append(instance)
        return instances
    except ClientError as e:
        print(f"Error al listar las instancias: {e.response['Error']['Message']}")
        return []

def list_security_groups():
    """
    Lista todos los grupos de seguridad en EC2.

    :return: Lista de grupos de seguridad si la operación es exitosa, lista vacía en caso de error.
    """
    try:
        response = ec2_client.describe_security_groups()
        return response['SecurityGroups']
    except ClientError as e:
        print(f"Error al listar los grupos de seguridad: {e.response['Error']['Message']}")
        return []

def main():
    # Definir IDs de instancia y grupo de seguridad para pruebas
    instance_id = 'i-0abcd1234efgh5678'
    group_name = 'MySecurityGroup'
    description = 'My security group description'
    vpc_id = 'vpc-0abcd1234efgh5678'

    # Crear un grupo de seguridad
    print("Creando grupo de seguridad...")
    security_group_id = create_security_group(group_name, description, vpc_id)
    print(f"ID del grupo de seguridad creado: {security_group_id}")

    # Listar grupos de seguridad
    print("Listando grupos de seguridad...")
    security_groups = list_security_groups()
    print(f"Grupos de seguridad disponibles: {security_groups}")

    # Describir un grupo de seguridad
    if security_group_id:
        print("Describiendo grupo de seguridad...")
        sg_details = describe_security_group(security_group_id)
        print(f"Detalles del grupo de seguridad: {sg_details}")

    # Iniciar una instancia
    print("Iniciando instancia...")
    start_response = start_instance(instance_id)
    print(f"Respuesta al iniciar la instancia: {start_response}")

    # Detener una instancia
    print("Deteniendo instancia...")
    stop_response = stop_instance(instance_id)
    print(f"Respuesta al detener la instancia: {stop_response}")

    # Reiniciar una instancia
    print("Reiniciando instancia...")
    reboot_response = reboot_instance(instance_id)
    print(f"Respuesta al reiniciar la instancia: {reboot_response}")

    # Describir una instancia
    print("Describiendo instancia...")
    instance_details = describe_instance(instance_id)
    print(f"Detalles de la instancia: {instance_details}")

    # Eliminar un grupo de seguridad
    if security_group_id:
        print("Eliminando grupo de seguridad...")
        delete_response = delete_security_group(security_group_id)
        print(f"Respuesta al eliminar el grupo de seguridad: {delete_response}")

    # Listar instancias
    print("Listando instancias...")
    instances = list_instances()
    print(f"Instancias disponibles: {instances}")

if __name__ == "__main__":
    main()

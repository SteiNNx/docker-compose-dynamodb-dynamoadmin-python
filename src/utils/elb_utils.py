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

# Inicializa el cliente de ELBv2
elb_client = boto3.client(
    'elbv2',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

def create_load_balancer(name, subnets, security_groups):
    """
    Crea un load balancer en AWS Elastic Load Balancing (ELB) v2.

    :param name: Nombre del load balancer.
    :param subnets: Lista de IDs de subredes para el load balancer.
    :param security_groups: Lista de IDs de grupos de seguridad asociados al load balancer.
    :return: Información del load balancer creado si la operación es exitosa, None en caso de error.
    """
    try:
        response = elb_client.create_load_balancer(
            Name=name,
            Subnets=subnets,
            SecurityGroups=security_groups,
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4'
        )
        return response['LoadBalancers'][0]
    except ClientError as e:
        print(f"Error al crear el load balancer {name}: {e.response['Error']['Message']}")
        return None

def delete_load_balancer(load_balancer_arn):
    """
    Elimina un load balancer en AWS Elastic Load Balancing (ELB) v2.

    :param load_balancer_arn: ARN del load balancer a eliminar.
    :return: Respuesta del servicio ELBv2 si la operación es exitosa, None en caso de error.
    """
    try:
        response = elb_client.delete_load_balancer(LoadBalancerArn=load_balancer_arn)
        return response
    except ClientError as e:
        print(f"Error al eliminar el load balancer {load_balancer_arn}: {e.response['Error']['Message']}")
        return None

def create_target_group(name, vpc_id, protocol='HTTP', port=80):
    """
    Crea un target group en AWS Elastic Load Balancing (ELB) v2.

    :param name: Nombre del target group.
    :param vpc_id: ID del VPC donde se creará el target group.
    :param protocol: Protocolo para el target group (por defecto 'HTTP').
    :param port: Puerto para el target group (por defecto 80).
    :return: Información del target group creado si la operación es exitosa, None en caso de error.
    """
    try:
        response = elb_client.create_target_group(
            Name=name,
            Protocol=protocol,
            Port=port,
            VpcId=vpc_id,
            TargetType='instance'
        )
        return response['TargetGroups'][0]
    except ClientError as e:
        print(f"Error al crear el target group {name}: {e.response['Error']['Message']}")
        return None

def register_targets(target_group_arn, targets):
    """
    Registra targets en un target group en AWS Elastic Load Balancing (ELB) v2.

    :param target_group_arn: ARN del target group.
    :param targets: Lista de targets a registrar (formato: [{'Id': 'i-1234567890abcdef0'}, ...]).
    :return: Respuesta del servicio ELBv2 si la operación es exitosa, None en caso de error.
    """
    try:
        response = elb_client.register_targets(TargetGroupArn=target_group_arn, Targets=targets)
        return response
    except ClientError as e:
        print(f"Error al registrar los targets en el target group {target_group_arn}: {e.response['Error']['Message']}")
        return None

def deregister_targets(target_group_arn, targets):
    """
    Desregistra targets de un target group en AWS Elastic Load Balancing (ELB) v2.

    :param target_group_arn: ARN del target group.
    :param targets: Lista de targets a desregistrar (formato: [{'Id': 'i-1234567890abcdef0'}, ...]).
    :return: Respuesta del servicio ELBv2 si la operación es exitosa, None en caso de error.
    """
    try:
        response = elb_client.deregister_targets(TargetGroupArn=target_group_arn, Targets=targets)
        return response
    except ClientError as e:
        print(f"Error al desregistrar los targets del target group {target_group_arn}: {e.response['Error']['Message']}")
        return None

def describe_load_balancer(load_balancer_arn):
    """
    Describe un load balancer en AWS Elastic Load Balancing (ELB) v2.

    :param load_balancer_arn: ARN del load balancer a describir.
    :return: Información del load balancer si la operación es exitosa, None en caso de error.
    """
    try:
        response = elb_client.describe_load_balancers(LoadBalancerArns=[load_balancer_arn])
        return response['LoadBalancers'][0] if 'LoadBalancers' in response and len(response['LoadBalancers']) > 0 else None
    except ClientError as e:
        print(f"Error al describir el load balancer {load_balancer_arn}: {e.response['Error']['Message']}")
        return None

def describe_target_group(target_group_arn):
    """
    Describe un target group en AWS Elastic Load Balancing (ELB) v2.

    :param target_group_arn: ARN del target group a describir.
    :return: Información del target group si la operación es exitosa, None en caso de error.
    """
    try:
        response = elb_client.describe_target_groups(TargetGroupArns=[target_group_arn])
        return response['TargetGroups'][0] if 'TargetGroups' in response and len(response['TargetGroups']) > 0 else None
    except ClientError as e:
        print(f"Error al describir el target group {target_group_arn}: {e.response['Error']['Message']}")
        return None

def list_load_balancers():
    """
    Lista todos los load balancers en AWS Elastic Load Balancing (ELB) v2.

    :return: Lista de load balancers si la operación es exitosa, lista vacía en caso de error.
    """
    try:
        response = elb_client.describe_load_balancers()
        return response['LoadBalancers']
    except ClientError as e:
        print(f"Error al listar los load balancers: {e.response['Error']['Message']}")
        return []

def list_target_groups():
    """
    Lista todos los target groups en AWS Elastic Load Balancing (ELB) v2.

    :return: Lista de target groups si la operación es exitosa, lista vacía en caso de error.
    """
    try:
        response = elb_client.describe_target_groups()
        return response['TargetGroups']
    except ClientError as e:
        print(f"Error al listar los target groups: {e.response['Error']['Message']}")
        return []

def main():
    # Definir IDs y nombres para pruebas
    load_balancer_name = 'my-load-balancer'
    subnets = ['subnet-0abcd1234efgh5678', 'subnet-1abcd1234efgh5678']
    security_groups = ['sg-0abcd1234efgh5678']
    vpc_id = 'vpc-0abcd1234efgh5678'
    target_group_name = 'my-target-group'
    instance_id = 'i-0abcd1234efgh5678'

    # Crear un load balancer
    print("Creando load balancer...")
    load_balancer = create_load_balancer(load_balancer_name, subnets, security_groups)
    print(f"Load balancer creado: {load_balancer}")

    # Listar load balancers
    print("Listando load balancers...")
    load_balancers = list_load_balancers()
    print(f"Load balancers disponibles: {load_balancers}")

    # Describir un load balancer
    if load_balancer:
        print("Describiendo load balancer...")
        lb_details = describe_load_balancer(load_balancer['LoadBalancerArn'])
        print(f"Detalles del load balancer: {lb_details}")

    # Crear un target group
    print("Creando target group...")
    target_group = create_target_group(target_group_name, vpc_id)
    print(f"Target group creado: {target_group}")

    # Registrar targets en el target group
    if target_group:
        print("Registrando targets en el target group...")
        register_response = register_targets(target_group['TargetGroupArn'], [{'Id': instance_id}])
        print(f"Respuesta al registrar targets: {register_response}")

    # Desregistrar targets del target group
    if target_group:
        print("Desregistrando targets del target group...")
        deregister_response = deregister_targets(target_group['TargetGroupArn'], [{'Id': instance_id}])
        print(f"Respuesta al desregistrar targets: {deregister_response}")

    # Eliminar el load balancer
    if load_balancer:
        print("Eliminando load balancer...")
        delete_response = delete_load_balancer(load_balancer['LoadBalancerArn'])
        print(f"Respuesta al eliminar el load balancer: {delete_response}")

if __name__ == "__main__":
    main()

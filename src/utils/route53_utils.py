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

# Inicializa el cliente de Route 53
route53_client = boto3.client(
    'route53',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para crear una zona hospedada
def create_hosted_zone(domain_name):
    try:
        response = route53_client.create_hosted_zone(
            Name=domain_name,
            CallerReference=str(hash(domain_name))
        )
        return response['HostedZone']
    except ClientError as e:
        print(f"Error al crear la zona hospedada {domain_name}: {e.response['Error']['Message']}")
        return None

# Método para eliminar una zona hospedada
def delete_hosted_zone(zone_id):
    try:
        response = route53_client.delete_hosted_zone(Id=zone_id)
        return response
    except ClientError as e:
        print(f"Error al eliminar la zona hospedada {zone_id}: {e.response['Error']['Message']}")
        return None

# Método para listar los conjuntos de registros en una zona hospedada
def list_record_sets(zone_id):
    try:
        response = route53_client.list_resource_record_sets(HostedZoneId=zone_id)
        return response['ResourceRecordSets']
    except ClientError as e:
        print(f"Error al listar los registros en la zona {zone_id}: {e.response['Error']['Message']}")
        return None

# Método para crear un registro en una zona hospedada
def create_record(zone_id, record_name, record_type, record_value, ttl=60):
    try:
        response = route53_client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': record_name,
                            'Type': record_type,
                            'TTL': ttl,
                            'ResourceRecords': [
                                {'Value': record_value}
                            ]
                        }
                    }
                ]
            }
        )
        return response
    except ClientError as e:
        print(f"Error al crear el registro {record_name} en la zona {zone_id}: {e.response['Error']['Message']}")
        return None

# Método para eliminar un registro de una zona hospedada
def delete_record(zone_id, record_name, record_type, record_value, ttl=60):
    try:
        response = route53_client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': record_name,
                            'Type': record_type,
                            'TTL': ttl,
                            'ResourceRecords': [
                                {'Value': record_value}
                            ]
                        }
                    }
                ]
            }
        )
        return response
    except ClientError as e:
        print(f"Error al eliminar el registro {record_name} en la zona {zone_id}: {e.response['Error']['Message']}")
        return None

# Método para actualizar un registro en una zona hospedada
def update_record(zone_id, record_name, record_type, old_value, new_value, ttl=60):
    try:
        response = route53_client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': record_name,
                            'Type': record_type,
                            'TTL': ttl,
                            'ResourceRecords': [
                                {'Value': old_value}
                            ]
                        }
                    },
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': record_name,
                            'Type': record_type,
                            'TTL': ttl,
                            'ResourceRecords': [
                                {'Value': new_value}
                            ]
                        }
                    }
                ]
            }
        )
        return response
    except ClientError as e:
        print(f"Error al actualizar el registro {record_name} en la zona {zone_id}: {e.response['Error']['Message']}")
        return None

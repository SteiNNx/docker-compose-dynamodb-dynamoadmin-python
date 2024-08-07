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

# Inicializa el cliente de Redshift
redshift_client = boto3.client(
    'redshift',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para crear un cluster de Redshift
def create_cluster(cluster_identifier, db_name, master_username, master_password, node_type='dc2.large', cluster_type='single-node'):
    try:
        response = redshift_client.create_cluster(
            ClusterIdentifier=cluster_identifier,
            DBName=db_name,
            MasterUsername=master_username,
            MasterUserPassword=master_password,
            NodeType=node_type,
            ClusterType=cluster_type
        )
        return response
    except ClientError as e:
        print(f"Error al crear el cluster {cluster_identifier}: {e.response['Error']['Message']}")
        return None

# Método para eliminar un cluster de Redshift
def delete_cluster(cluster_identifier, skip_final_snapshot=True):
    try:
        response = redshift_client.delete_cluster(
            ClusterIdentifier=cluster_identifier,
            SkipFinalSnapshot=skip_final_snapshot
        )
        return response
    except ClientError as e:
        print(f"Error al eliminar el cluster {cluster_identifier}: {e.response['Error']['Message']}")
        return None

# Método para describir un cluster de Redshift
def describe_cluster(cluster_identifier):
    try:
        response = redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)
        return response['Clusters'][0]
    except ClientError as e:
        print(f"Error al describir el cluster {cluster_identifier}: {e.response['Error']['Message']}")
        return None

# Método para listar clusters de Redshift
def list_clusters():
    try:
        response = redshift_client.describe_clusters()
        return response['Clusters']
    except ClientError as e:
        print(f"Error al listar los clusters: {e.response['Error']['Message']}")
        return None

# Método para modificar un cluster de Redshift
def modify_cluster(cluster_identifier, node_type=None, cluster_type=None):
    try:
        response = redshift_client.modify_cluster(
            ClusterIdentifier=cluster_identifier,
            NodeType=node_type,
            ClusterType=cluster_type
        )
        return response
    except ClientError as e:
        print(f"Error al modificar el cluster {cluster_identifier}: {e.response['Error']['Message']}")
        return None

# Método para crear un snapshot de un cluster de Redshift
def create_snapshot(snapshot_identifier, cluster_identifier):
    try:
        response = redshift_client.create_cluster_snapshot(
            SnapshotIdentifier=snapshot_identifier,
            ClusterIdentifier=cluster_identifier
        )
        return response
    except ClientError as e:
        print(f"Error al crear el snapshot {snapshot_identifier}: {e.response['Error']['Message']}")
        return None

# Método para eliminar un snapshot de Redshift
def delete_snapshot(snapshot_identifier):
    try:
        response = redshift_client.delete_cluster_snapshot(
            SnapshotIdentifier=snapshot_identifier
        )
        return response
    except ClientError as e:
        print(f"Error al eliminar el snapshot {snapshot_identifier}: {e.response['Error']['Message']}")
        return None

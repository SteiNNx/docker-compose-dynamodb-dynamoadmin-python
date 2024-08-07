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

# Inicializa el cliente de RDS
rds_client = boto3.client(
    'rds',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para crear una instancia RDS
def create_rds_instance(db_identifier, db_name, master_username, master_password):
    try:
        response = rds_client.create_db_instance(
            DBInstanceIdentifier=db_identifier,
            DBName=db_name,
            MasterUsername=master_username,
            MasterUserPassword=master_password,
            DBInstanceClass='db.t2.micro',
            Engine='mysql',
            AllocatedStorage=20
        )
        return response
    except ClientError as e:
        print(f"Error al crear la instancia RDS {db_identifier}: {e.response['Error']['Message']}")
        return None

# Método para eliminar una instancia RDS
def delete_rds_instance(db_identifier):
    try:
        response = rds_client.delete_db_instance(
            DBInstanceIdentifier=db_identifier,
            SkipFinalSnapshot=True
        )
        return response
    except ClientError as e:
        print(f"Error al eliminar la instancia RDS {db_identifier}: {e.response['Error']['Message']}")
        return None

# Método para describir una instancia RDS
def describe_rds_instance(db_identifier):
    try:
        response = rds_client.describe_db_instances(DBInstanceIdentifier=db_identifier)
        return response['DBInstances'][0]
    except ClientError as e:
        print(f"Error al describir la instancia RDS {db_identifier}: {e.response['Error']['Message']}")
        return None

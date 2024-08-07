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

# Inicializa el cliente de Glue
glue_client = boto3.client(
    'glue',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para crear un trabajo Glue
def create_glue_job(job_name, role, script_location):
    try:
        response = glue_client.create_job(
            Name=job_name,
            Role=role,
            Command={
                'Name': 'glueetl',
                'ScriptLocation': script_location
            }
        )
        return response
    except ClientError as e:
        print(f"Error al crear el trabajo Glue {job_name}: {e.response['Error']['Message']}")
        return None

# Método para iniciar un trabajo Glue
def start_glue_job(job_name, arguments={}):
    try:
        response = glue_client.start_job_run(JobName=job_name, Arguments=arguments)
        return response['JobRunId']
    except ClientError as e:
        print(f"Error al iniciar el trabajo Glue {job_name}: {e.response['Error']['Message']}")
        return None

# Método para obtener el estado de un trabajo Glue
def get_job_run_status(job_name, job_run_id):
    try:
        response = glue_client.get_job_run(JobName=job_name, RunId=job_run_id)
        return response['JobRun']['JobRunState']
    except ClientError as e:
        print(f"Error al obtener el estado del trabajo Glue {job_name} (RunId: {job_run_id}): {e.response['Error']['Message']}")
        return None

# Método para describir un trabajo Glue
def describe_glue_job(job_name):
    try:
        response = glue_client.get_job(JobName=job_name)
        return response['Job']
    except ClientError as e:
        print(f"Error al describir el trabajo Glue {job_name}: {e.response['Error']['Message']}")
        return None

# Método para listar trabajos Glue
def list_glue_jobs():
    try:
        response = glue_client.list_jobs()
        return response['JobNames']
    except ClientError as e:
        print(f"Error al listar los trabajos Glue: {e.response['Error']['Message']}")
        return []

# Método para detener un trabajo Glue en ejecución
def stop_glue_job_run(job_name, job_run_id):
    try:
        response = glue_client.batch_stop_job_run(
            JobName=job_name,
            JobRunIds=[job_run_id]
        )
        return response
    except ClientError as e:
        print(f"Error al detener el trabajo Glue {job_name} (RunId: {job_run_id}): {e.response['Error']['Message']}")
        return None

# Método para listar los runs de un trabajo Glue
def list_glue_job_runs(job_name):
    try:
        response = glue_client.get_job_runs(JobName=job_name)
        return response['JobRuns']
    except ClientError as e:
        print(f"Error al listar los runs del trabajo Glue {job_name}: {e.response['Error']['Message']}")
        return []

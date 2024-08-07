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

# Inicializa el cliente de EMR
emr_client = boto3.client(
    'emr',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para crear un clúster EMR
def create_emr_cluster(name, release_label, instance_type, instance_count, log_uri):
    try:
        response = emr_client.run_job_flow(
            Name=name,
            LogUri=log_uri,
            ReleaseLabel=release_label,
            Instances={
                'InstanceGroups': [
                    {
                        'Name': 'Master nodes',
                        'InstanceRole': 'MASTER',
                        'InstanceType': instance_type,
                        'InstanceCount': 1,
                    },
                    {
                        'Name': 'Core nodes',
                        'InstanceRole': 'CORE',
                        'InstanceType': instance_type,
                        'InstanceCount': instance_count - 1,
                    }
                ],
                'Ec2KeyName': 'your-ec2-key-name',
                'KeepJobFlowAliveWhenNoSteps': True,
                'TerminationProtected': False,
            },
            Applications=[{'Name': 'Hadoop'}, {'Name': 'Spark'}],
            JobFlowRole='EMR_EC2_DefaultRole',
            ServiceRole='EMR_DefaultRole'
        )
        return response['JobFlowId']
    except ClientError as e:
        print(f"Error al crear el clúster EMR {name}: {e.response['Error']['Message']}")
        return None

# Método para terminar un clúster EMR
def terminate_emr_cluster(cluster_id):
    try:
        response = emr_client.terminate_job_flows(JobFlowIds=[cluster_id])
        return response
    except ClientError as e:
        print(f"Error al terminar el clúster EMR {cluster_id}: {e.response['Error']['Message']}")
        return None

# Método para listar clústeres EMR
def list_emr_clusters():
    try:
        response = emr_client.list_clusters(ClusterStates=['STARTING', 'BOOTSTRAPPING', 'RUNNING', 'WAITING'])
        return response['Clusters']
    except ClientError as e:
        print(f"Error al listar los clústeres EMR: {e.response['Error']['Message']}")
        return []

# Método para describir un clúster EMR
def describe_emr_cluster(cluster_id):
    try:
        response = emr_client.describe_cluster(ClusterId=cluster_id)
        return response['Cluster']
    except ClientError as e:
        print(f"Error al describir el clúster EMR {cluster_id}: {e.response['Error']['Message']}")
        return None

# Método para agregar un paso a un clúster EMR
def add_step_to_emr_cluster(cluster_id, name, action_on_failure, hadoop_jar_step):
    try:
        response = emr_client.add_job_flow_steps(
            JobFlowId=cluster_id,
            Steps=[
                {
                    'Name': name,
                    'ActionOnFailure': action_on_failure,
                    'HadoopJarStep': hadoop_jar_step
                }
            ]
        )
        return response['StepIds']
    except ClientError as e:
        print(f"Error al agregar el paso al clúster EMR {cluster_id}: {e.response['Error']['Message']}")
        return None

# Método para eliminar un paso de un clúster EMR
def remove_step_from_emr_cluster(cluster_id, step_id):
    try:
        response = emr_client.remove_job_flow_steps(
            JobFlowId=cluster_id,
            StepIds=[step_id]
        )
        return response
    except ClientError as e:
        print(f"Error al eliminar el paso {step_id} del clúster EMR {cluster_id}: {e.response['Error']['Message']}")
        return None

# Método para describir los pasos de un clúster EMR
def describe_emr_steps(cluster_id, step_ids):
    try:
        response = emr_client.describe_step(JobFlowId=cluster_id, StepId=step_ids)
        return response['Step']
    except ClientError as e:
        print(f"Error al describir el paso {step_ids} del clúster EMR {cluster_id}: {e.response['Error']['Message']}")
        return None

# Método para listar los pasos de un clúster EMR
def list_emr_steps(cluster_id):
    try:
        response = emr_client.list_steps(ClusterId=cluster_id)
        return response['Steps']
    except ClientError as e:
        print(f"Error al listar los pasos del clúster EMR {cluster_id}: {e.response['Error']['Message']}")
        return []

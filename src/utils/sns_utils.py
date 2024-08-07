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

# Inicializa el cliente de SNS
sns_client = boto3.client(
    'sns',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para crear un tema de SNS
def create_sns_topic(topic_name):
    try:
        response = sns_client.create_topic(Name=topic_name)
        return response['TopicArn']
    except ClientError as e:
        print(f"Error al crear el tema {topic_name}: {e.response['Error']['Message']}")
        return None

# Método para publicar un mensaje en un tema de SNS
def publish_to_topic(topic_arn, message):
    try:
        response = sns_client.publish(TopicArn=topic_arn, Message=message)
        return response
    except ClientError as e:
        print(f"Error al publicar en el tema {topic_arn}: {e.response['Error']['Message']}")
        return None

# Método para suscribirse a un tema de SNS
def subscribe_to_topic(topic_arn, protocol, endpoint):
    try:
        response = sns_client.subscribe(TopicArn=topic_arn, Protocol=protocol, Endpoint=endpoint)
        return response['SubscriptionArn']
    except ClientError as e:
        print(f"Error al suscribirse al tema {topic_arn}: {e.response['Error']['Message']}")
        return None

# Método para listar las suscripciones a un tema de SNS
def list_subscriptions_by_topic(topic_arn):
    try:
        response = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
        return response['Subscriptions']
    except ClientError as e:
        print(f"Error al listar las suscripciones del tema {topic_arn}: {e.response['Error']['Message']}")
        return None

# Método para eliminar una suscripción de SNS
def unsubscribe(subscription_arn):
    try:
        response = sns_client.unsubscribe(SubscriptionArn=subscription_arn)
        return response
    except ClientError as e:
        print(f"Error al cancelar la suscripción {subscription_arn}: {e.response['Error']['Message']}")
        return None

# Método para eliminar un tema de SNS
def delete_sns_topic(topic_arn):
    try:
        response = sns_client.delete_topic(TopicArn=topic_arn)
        return response
    except ClientError as e:
        print(f"Error al eliminar el tema {topic_arn}: {e.response['Error']['Message']}")
        return None

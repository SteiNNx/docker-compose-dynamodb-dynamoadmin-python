import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de variables de entorno
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'fakemykeyid')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'fakemysecretaccesskey')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', 'fakemysessiontoken')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Inicializar el cliente de Glue
glue_client = boto3.client(
    'glue',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

def create_crawler(name, role, database_name, table_prefix, targets):
    """
    Crea un nuevo crawler en AWS Glue.
    
    :param name: Nombre del crawler.
    :param role: Rol de IAM que el crawler usará.
    :param database_name: Nombre de la base de datos en Glue.
    :param table_prefix: Prefijo para las tablas creadas por el crawler.
    :param targets: Objetivos de datos del crawler, como una lista de ubicaciones de S3.
    """
    try:
        glue_client.create_crawler(
            Name=name,
            Role=role,
            DatabaseName=database_name,
            TablePrefix=table_prefix,
            Targets=targets
        )
        print(f"Crawler {name} creado exitosamente.")
    except ClientError as e:
        print(f"Error al crear el crawler: {e.response['Error']['Message']}")

def start_crawler(name):
    """
    Inicia un crawler existente en AWS Glue.
    
    :param name: Nombre del crawler a iniciar.
    """
    try:
        glue_client.start_crawler(Name=name)
        print(f"Crawler {name} iniciado exitosamente.")
    except ClientError as e:
        print(f"Error al iniciar el crawler: {e.response['Error']['Message']}")

def stop_crawler(name):
    """
    Detiene un crawler en ejecución en AWS Glue.
    
    :param name: Nombre del crawler a detener.
    """
    try:
        glue_client.stop_crawler(Name=name)
        print(f"Crawler {name} detenido exitosamente.")
    except ClientError as e:
        print(f"Error al detener el crawler: {e.response['Error']['Message']}")

def update_crawler(name, role=None, database_name=None, table_prefix=None, targets=None):
    """
    Actualiza un crawler existente en AWS Glue.
    
    :param name: Nombre del crawler a actualizar.
    :param role: Nuevo rol de IAM (opcional).
    :param database_name: Nuevo nombre de la base de datos (opcional).
    :param table_prefix: Nuevo prefijo de tabla (opcional).
    :param targets: Nuevos objetivos de datos (opcional).
    """
    try:
        update_params = {'Name': name}
        if role:
            update_params['Role'] = role
        if database_name:
            update_params['DatabaseName'] = database_name
        if table_prefix:
            update_params['TablePrefix'] = table_prefix
        if targets:
            update_params['Targets'] = targets
        
        glue_client.update_crawler(**update_params)
        print(f"Crawler {name} actualizado exitosamente.")
    except ClientError as e:
        print(f"Error al actualizar el crawler: {e.response['Error']['Message']}")

def list_crawlers():
    """
    Lista todos los crawlers disponibles en AWS Glue.
    
    :return: Lista de nombres de crawlers.
    """
    try:
        response = glue_client.list_crawlers()
        crawler_names = response.get('CrawlerNames', [])
        print(f"Crawlers disponibles: {crawler_names}")
        return crawler_names
    except ClientError as e:
        print(f"Error al listar crawlers: {e.response['Error']['Message']}")
        return []

def get_crawler_state(name):
    """
    Obtiene el estado de un crawler específico en AWS Glue.
    
    :param name: Nombre del crawler.
    :return: Estado del crawler.
    """
    try:
        response = glue_client.get_crawler(Name=name)
        state = response['Crawler']['State']
        print(f"Estado del crawler {name}: {state}")
        return state
    except ClientError as e:
        print(f"Error al obtener el estado del crawler: {e.response['Error']['Message']}")
        return None

def main():
    """
    Función principal para demostrar el uso de los métodos definidos.
    """
    # Crear un crawler
    create_crawler(
        name='example-crawler',
        role='arn:aws:iam::123456789012:role/AWSGlueServiceRole',
        database_name='example-database',
        table_prefix='example_',
        targets={'S3Targets': [{'Path': 's3://example-bucket/path/'}]}
    )
    
    # Listar crawlers
    crawlers = list_crawlers()
    
    if crawlers:
        # Iniciar el primer crawler de la lista
        start_crawler(crawlers[0])
        
        # Obtener el estado del primer crawler
        get_crawler_state(crawlers[0])
        
        # Detener el primer crawler
        stop_crawler(crawlers[0])
        
        # Actualizar el primer crawler
        update_crawler(
            name=crawlers[0],
            role='arn:aws:iam::123456789012:role/NewGlueRole',
            database_name='new-database',
            table_prefix='new_'
        )

if __name__ == '__main__':
    main()

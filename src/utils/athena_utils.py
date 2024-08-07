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

# Inicializa el cliente de Athena
athena_client = boto3.client(
    'athena',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

def start_query_execution(query, database, output_location):
    """
    Inicia la ejecución de una consulta en Athena.
    :param query: Cadena de consulta SQL para ejecutar.
    :param database: Nombre de la base de datos en Athena.
    :param output_location: Ubicación S3 para almacenar los resultados de la consulta.
    :return: ID de ejecución de la consulta.
    """
    try:
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': output_location}
        )
        return response['QueryExecutionId']
    except ClientError as e:
        print(f"Error al iniciar la ejecución de la consulta: {e.response['Error']['Message']}")
        return None

def get_query_execution_status(query_execution_id):
    """
    Obtiene el estado de la ejecución de una consulta en Athena.
    :param query_execution_id: ID de ejecución de la consulta.
    :return: Estado de la consulta (e.g., 'RUNNING', 'SUCCEEDED', 'FAILED').
    """
    try:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        return response['QueryExecution']['Status']['State']
    except ClientError as e:
        print(f"Error al obtener el estado de ejecución de la consulta: {e.response['Error']['Message']}")
        return None

def get_query_results(query_execution_id):
    """
    Obtiene los resultados de la consulta ejecutada en Athena.
    :param query_execution_id: ID de ejecución de la consulta.
    :return: ResultSet que contiene los resultados de la consulta.
    """
    try:
        response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        return response['ResultSet']
    except ClientError as e:
        print(f"Error al obtener los resultados de la consulta: {e.response['Error']['Message']}")
        return None

def get_query_results_paginated(query_execution_id):
    """
    Obtiene los resultados de la consulta ejecutada en Athena con paginación.
    :param query_execution_id: ID de ejecución de la consulta.
    :return: Lista de filas de resultados de la consulta.
    """
    try:
        paginator = athena_client.get_paginator('get_query_results')
        page_iterator = paginator.paginate(QueryExecutionId=query_execution_id)
        results = []
        for page in page_iterator:
            results.extend(page['ResultSet']['Rows'])
        return results
    except ClientError as e:
        print(f"Error al obtener los resultados paginados de la consulta: {e.response['Error']['Message']}")
        return None

def stop_query_execution(query_execution_id):
    """
    Cancela una consulta en ejecución.
    :param query_execution_id: ID de ejecución de la consulta a cancelar.
    """
    try:
        athena_client.stop_query_execution(QueryExecutionId=query_execution_id)
        print(f"Consulta con ID {query_execution_id} cancelada.")
    except ClientError as e:
        print(f"Error al cancelar la consulta: {e.response['Error']['Message']}")

def describe_query_execution(query_execution_id):
    """
    Obtiene detalles sobre la ejecución de una consulta en Athena.
    :param query_execution_id: ID de ejecución de la consulta.
    :return: Detalles de la ejecución de la consulta.
    """
    try:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        return response['QueryExecution']
    except ClientError as e:
        print(f"Error al describir la ejecución de la consulta: {e.response['Error']['Message']}")
        return None

def list_query_executions(start_time, end_time):
    """
    Lista las ejecuciones de consultas en Athena dentro de un rango de tiempo.
    :param start_time: Tiempo de inicio en formato ISO 8601 (e.g., '2024-01-01T00:00:00Z').
    :param end_time: Tiempo de fin en formato ISO 8601 (e.g., '2024-01-02T00:00:00Z').
    :return: Lista de IDs de ejecuciones de consultas.
    """
    try:
        response = athena_client.list_query_executions(
            StartTime=start_time,
            EndTime=end_time
        )
        return response['QueryExecutionIds']
    except ClientError as e:
        print(f"Error al listar ejecuciones de consultas: {e.response['Error']['Message']}")
        return None

def list_databases():
    """
    Lista las bases de datos disponibles en Athena.
    :return: Lista de nombres de bases de datos.
    """
    try:
        response = athena_client.list_databases(CatalogName='AwsDataCatalog')
        return [db['Name'] for db in response['DatabaseList']]
    except ClientError as e:
        print(f"Error al listar bases de datos: {e.response['Error']['Message']}")
        return None

def list_tables(database_name):
    """
    Lista las tablas en una base de datos de Athena.
    :param database_name: Nombre de la base de datos en Athena.
    :return: Lista de nombres de tablas en la base de datos.
    """
    try:
        response = athena_client.list_tables(CatalogName='AwsDataCatalog', DatabaseName=database_name)
        return [table['Name'] for table in response['TableList']]
    except ClientError as e:
        print(f"Error al listar tablas en la base de datos {database_name}: {e.response['Error']['Message']}")
        return None

def main():
    """
    Método principal que llama a cada una de las funciones para demostrar su uso.
    """
    # Define los parámetros que se usarán en las funciones
    query = "SELECT * FROM your_table LIMIT 10;"
    database = "your_database"
    output_location = "s3://your-bucket/athena-results/"
    query_execution_id = None
    start_time = "2024-01-01T00:00:00Z"
    end_time = "2024-01-02T00:00:00Z"

    ### Ejecutar una consulta en Athena
    print("Iniciando la ejecución de la consulta...")
    query_execution_id = start_query_execution(query, database, output_location)
    if query_execution_id:
        print(f"Consulta iniciada con ID: {query_execution_id}")

    ### Obtener el estado de la consulta
    print("Obteniendo el estado de la consulta...")
    status = get_query_execution_status(query_execution_id)
    print(f"Estado de la consulta: {status}")

    ### Obtener los resultados de la consulta
    print("Obteniendo los resultados de la consulta...")
    if status == 'SUCCEEDED':
        results = get_query_results(query_execution_id)
        print("Resultados de la consulta:", results)

        ### Obtener los resultados paginados
        print("Obteniendo resultados paginados...")
        paginated_results = get_query_results_paginated(query_execution_id)
        print("Resultados paginados:", paginated_results)

    ### Cancelar una consulta en ejecución (descomentar si es necesario)
    # print("Cancelando la consulta en ejecución...")
    # stop_query_execution(query_execution_id)

    ### Describir la ejecución de la consulta
    print("Describiendo la ejecución de la consulta...")
    description = describe_query_execution(query_execution_id)
    print("Descripción de la ejecución:", description)

    ### Listar ejecuciones de consultas en un rango de tiempo
    print("Listando ejecuciones de consultas...")
    query_executions = list_query_executions(start_time, end_time)
    print("IDs de ejecuciones de consultas:", query_executions)

    ### Listar bases de datos disponibles en Athena
    print("Listando bases de datos...")
    databases = list_databases()
    print("Bases de datos disponibles:", databases)

    ### Listar tablas en una base de datos específica
    print("Listando tablas en la base de datos...")
    if databases:
        tables = list_tables(database)
        print(f"Tablas en la base de datos {database}:", tables)

# Ejecutar la función main si este archivo se ejecuta directamente
if __name__ == "__main__":
    main()

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de variables de entorno para DynamoDB
DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT', 'http://dynamodb-local:8000')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'fakemykeyid')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'fakemysecretaccesskey')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', 'fakemysessiontoken')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Inicializa el cliente y recurso de DynamoDB
dynamodb_client = boto3.client(
    'dynamodb',
    region_name=AWS_REGION,
    endpoint_url=DYNAMODB_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

dynamodb_resource = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    endpoint_url=DYNAMODB_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

def create_table(table_name, key_schema, attribute_definitions, provisioned_throughput):
    """
    Crea una nueva tabla en DynamoDB.

    :param table_name: Nombre de la tabla.
    :param key_schema: Esquema de claves de la tabla.
    :param attribute_definitions: Definiciones de atributos para la tabla.
    :param provisioned_throughput: Configuración de capacidad provisionada.
    :return: La tabla creada o None si ocurre un error.
    """
    try:
        table = dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput
        )
        return table
    except ClientError as e:
        print(f"Error al crear la tabla {table_name}: {e.response['Error']['Message']}")
        return None

def list_tables():
    """
    Lista todas las tablas disponibles en DynamoDB.

    :return: Lista de nombres de tablas.
    """
    try:
        tables = dynamodb_client.list_tables()
        return tables.get('TableNames', [])
    except ClientError as e:
        print(f"Error al listar tablas: {e.response['Error']['Message']}")
        return []

def get_item(table_name, key):
    """
    Obtiene un ítem de una tabla en DynamoDB.

    :param table_name: Nombre de la tabla.
    :param key: Clave del ítem a obtener.
    :return: El ítem si se encuentra, None en caso contrario.
    """
    try:
        response = dynamodb_client.get_item(TableName=table_name, Key=key)
        return response.get('Item', None)
    except ClientError as e:
        print(f"Error al obtener el ítem de la tabla {table_name}: {e.response['Error']['Message']}")
        return None

def put_item(table_name, item):
    """
    Añade un ítem a una tabla en DynamoDB.

    :param table_name: Nombre de la tabla.
    :param item: Ítem a añadir.
    """
    try:
        dynamodb_client.put_item(TableName=table_name, Item=item)
        print(f"Ítem añadido exitosamente en la tabla {table_name}")
    except ClientError as e:
        print(f"Error al añadir el ítem en la tabla {table_name}: {e.response['Error']['Message']}")

def update_item(table_name, key, update_expression, expression_attribute_values):
    """
    Actualiza un ítem en una tabla de DynamoDB.

    :param table_name: Nombre de la tabla.
    :param key: Clave del ítem a actualizar.
    :param update_expression: Expresión de actualización.
    :param expression_attribute_values: Valores de los atributos de la expresión.
    :return: Respuesta de la actualización o None si ocurre un error.
    """
    try:
        response = dynamodb_client.update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return response
    except ClientError as e:
        print(f"Error al actualizar el ítem en la tabla {table_name}: {e.response['Error']['Message']}")
        return None

def delete_item(table_name, key):
    """
    Elimina un ítem de una tabla en DynamoDB.

    :param table_name: Nombre de la tabla.
    :param key: Clave del ítem a eliminar.
    """
    try:
        dynamodb_client.delete_item(TableName=table_name, Key=key)
        print(f"Ítem eliminado exitosamente de la tabla {table_name}")
    except ClientError as e:
        print(f"Error al eliminar el ítem de la tabla {table_name}: {e.response['Error']['Message']}")

def scan_table(table_name):
    """
    Escanea una tabla en DynamoDB y devuelve todos los ítems.

    :param table_name: Nombre de la tabla.
    :return: Lista de ítems en la tabla.
    """
    try:
        response = dynamodb_client.scan(TableName=table_name)
        return response.get('Items', [])
    except ClientError as e:
        print(f"Error al escanear la tabla {table_name}: {e.response['Error']['Message']}")
        return []

def enable_ttl(table_name, ttl_field_name):
    """
    Habilita la función de Tiempo de Vida (TTL) en una tabla de DynamoDB.

    :param table_name: Nombre de la tabla.
    :param ttl_field_name: Nombre del campo de TTL.
    :return: Respuesta de la actualización de TTL o None si ocurre un error.
    """
    try:
        response = dynamodb_client.update_time_to_live(
            TableName=table_name,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': ttl_field_name
            }
        )
        print(f"TTL habilitado en la tabla {table_name}")
        return response
    except ClientError as e:
        print(f"Error al habilitar TTL en la tabla {table_name}: {e.response['Error']['Message']}")
        return None

def describe_table(table_name):
    """
    Describe una tabla en DynamoDB.

    :param table_name: Nombre de la tabla.
    :return: Información de la tabla o un diccionario vacío si ocurre un error.
    """
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        return response.get('Table', {})
    except ClientError as e:
        print(f"Error al describir la tabla {table_name}: {e.response['Error']['Message']}")
        return {}

def batch_write_items(table_name, items):
    """
    Escribe un batch de ítems en una tabla de DynamoDB.

    :param table_name: Nombre de la tabla.
    :param items: Lista de ítems a escribir.
    """
    try:
        with dynamodb_resource.Table(table_name).batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        print(f"Batch de ítems escritos exitosamente en la tabla {table_name}")
    except ClientError as e:
        print(f"Error al hacer el batch write en la tabla {table_name}: {e.response['Error']['Message']}")

def main():
    # Definir nombre de la tabla
    table_name = 'TestTable'
    
    # Definir esquema de claves y atributos
    key_schema = [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ]
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        }
    ]
    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
    
    # Crear la tabla
    print("Creando la tabla...")
    create_table(table_name, key_schema, attribute_definitions, provisioned_throughput)
    
    # Listar tablas
    print("Listando tablas...")
    tables = list_tables()
    print(f"Tablas disponibles: {tables}")
    
    # Poner un ítem
    print("Añadiendo ítem...")
    item = {
        'id': {'S': '123'},
        'data': {'S': 'sample data'}
    }
    put_item(table_name, item)
    
    # Obtener un ítem
    print("Obteniendo ítem...")
    key = {'id': {'S': '123'}}
    retrieved_item = get_item(table_name, key)
    print(f"Ítem recuperado: {retrieved_item}")
    
    # Actualizar un ítem
    print("Actualizando ítem...")
    update_expression = 'SET data = :data'
    expression_attribute_values = {':data': {'S': 'updated data'}}
    update_item(table_name, key, update_expression, expression_attribute_values)
    
    # Escanear tabla
    print("Escaneando tabla...")
    items = scan_table(table_name)
    print(f"Ítems en la tabla: {items}")
    
    # Habilitar TTL
    print("Habilitando TTL...")
    enable_ttl(table_name, 'ttl')
    
    # Describir tabla
    print("Describiendo tabla...")
    table_description = describe_table(table_name)
    print(f"Descripción de la tabla: {table_description}")
    
    # Eliminar ítem
    print("Eliminando ítem...")
    delete_item(table_name, key)
    
    # Hacer batch write
    print("Haciendo batch write...")
    items_to_write = [
        {'id': {'S': '456'}, 'data': {'S': 'batch data 1'}},
        {'id': {'S': '789'}, 'data': {'S': 'batch data 2'}}
    ]
    batch_write_items(table_name, items_to_write)

if __name__ == "__main__":
    main()

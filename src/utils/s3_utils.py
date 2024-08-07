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

# Inicializar el cliente S3
s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Método para subir un archivo a S3
def upload_file(file_name, bucket, object_name=None):
    """Sube un archivo a un bucket de S3."""
    try:
        if object_name is None:
            object_name = os.path.basename(file_name)
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"Archivo {file_name} subido exitosamente a {bucket}/{object_name}")
    except ClientError as e:
        print(f"Error al subir el archivo a S3: {e.response['Error']['Message']}")

# Método para descargar un archivo de S3
def download_file(bucket, object_name, file_name):
    """Descarga un archivo desde un bucket de S3."""
    try:
        s3_client.download_file(bucket, object_name, file_name)
        print(f"Archivo {object_name} descargado exitosamente de {bucket} a {file_name}")
    except ClientError as e:
        print(f"Error al descargar el archivo de S3: {e.response['Error']['Message']}")

# Método para listar objetos en un bucket de S3
def list_objects(bucket, prefix=''):
    """Lista los objetos en un bucket de S3."""
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]
    except ClientError as e:
        print(f"Error al listar objetos en S3: {e.response['Error']['Message']}")
        return []

# Método para eliminar un objeto de S3
def delete_object(bucket, object_name):
    """Elimina un objeto de un bucket de S3."""
    try:
        s3_client.delete_object(Bucket=bucket, Key=object_name)
        print(f"Objeto {object_name} eliminado exitosamente de {bucket}")
    except ClientError as e:
        print(f"Error al eliminar el objeto de S3: {e.response['Error']['Message']}")

# Método para copiar un objeto de S3 a otro bucket o nombre de objeto
def copy_object(source_bucket, source_object, dest_bucket, dest_object):
    """Copia un objeto de S3 a otro bucket o nombre de objeto."""
    try:
        copy_source = {'Bucket': source_bucket, 'Key': source_object}
        s3_client.copy(copy_source, dest_bucket, dest_object)
        print(f"Objeto copiado de {source_bucket}/{source_object} a {dest_bucket}/{dest_object}")
    except ClientError as e:
        print(f"Error al copiar el objeto en S3: {e.response['Error']['Message']}")

# Método para obtener el contenido de un archivo de texto de S3
def get_object_content(bucket, object_name):
    """Obtiene el contenido de un objeto de texto de S3."""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=object_name)
        content = response['Body'].read().decode('utf-8')
        return content
    except ClientError as e:
        print(f"Error al obtener el contenido del objeto de S3: {e.response['Error']['Message']}")
        return None

# Método para obtener la URL pública de un objeto de S3
def get_object_url(bucket, object_name):
    """Genera una URL pública para un objeto de S3."""
    try:
        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': bucket, 'Key': object_name},
                                               ExpiresIn=3600)
        return url
    except ClientError as e:
        print(f"Error al generar la URL de S3: {e.response['Error']['Message']}")
        return None

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de variables de entorno
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'fakemykeyid')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'fakemysecretaccesskey')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', 'fakemysessiontoken')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Inicializa el cliente de CloudWatch
cloudwatch_client = boto3.client(
    'cloudwatch',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

def create_alarm(alarm_name, metric_name, namespace, threshold, comparison_operator, evaluation_periods, period, statistic, actions_enabled=False):
    """
    Crea una alarma en AWS CloudWatch.
    :param alarm_name: Nombre de la alarma.
    :param metric_name: Nombre de la métrica.
    :param namespace: Espacio de nombres de la métrica.
    :param threshold: Umbral de la alarma.
    :param comparison_operator: Operador de comparación.
    :param evaluation_periods: Períodos de evaluación.
    :param period: Periodo de la métrica.
    :param statistic: Estadística de la métrica.
    :param actions_enabled: Si las acciones están habilitadas.
    :return: Respuesta de la creación de la alarma.
    """
    try:
        response = cloudwatch_client.put_metric_alarm(
            AlarmName=alarm_name,
            MetricName=metric_name,
            Namespace=namespace,
            Threshold=threshold,
            ComparisonOperator=comparison_operator,
            EvaluationPeriods=evaluation_periods,
            Period=period,
            Statistic=statistic,
            ActionsEnabled=actions_enabled
        )
        return response
    except ClientError as e:
        print(f"Error al crear la alarma {alarm_name}: {e.response['Error']['Message']}")
        return None

def put_metric_data(namespace, metric_name, value, dimensions=None, unit=None):
    """
    Publica datos de métricas en AWS CloudWatch.
    :param namespace: Espacio de nombres de la métrica.
    :param metric_name: Nombre de la métrica.
    :param value: Valor de la métrica.
    :param dimensions: Dimensiones opcionales de la métrica.
    :param unit: Unidad opcional de la métrica.
    :return: Respuesta de la publicación de datos de métricas.
    """
    try:
        response = cloudwatch_client.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Value': value,
                    'Dimensions': dimensions or [],
                    'Unit': unit or 'None'
                },
            ]
        )
        return response
    except ClientError as e:
        print(f"Error al publicar datos de métricas: {e.response['Error']['Message']}")
        return None

def get_metric_statistics(namespace, metric_name, start_time, end_time, period, statistics, dimensions=None):
    """
    Obtiene estadísticas de métricas en AWS CloudWatch.
    :param namespace: Espacio de nombres de la métrica.
    :param metric_name: Nombre de la métrica.
    :param start_time: Hora de inicio del periodo.
    :param end_time: Hora de fin del periodo.
    :param period: Periodo de la métrica.
    :param statistics: Estadísticas solicitadas.
    :param dimensions: Dimensiones opcionales de la métrica.
    :return: Datos de la métrica.
    """
    try:
        response = cloudwatch_client.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=[statistics],
            Dimensions=dimensions or []
        )
        return response['Datapoints']
    except ClientError as e:
        print(f"Error al obtener las estadísticas de la métrica {metric_name}: {e.response['Error']['Message']}")
        return []

def list_alarms():
    """
    Lista todas las alarmas en AWS CloudWatch.
    :return: Lista de alarmas métricas.
    """
    try:
        response = cloudwatch_client.describe_alarms()
        return response['MetricAlarms']
    except ClientError as e:
        print(f"Error al listar alarmas: {e.response['Error']['Message']}")
        return []

def describe_alarm(alarm_name):
    """
    Obtiene detalles de una alarma en AWS CloudWatch.
    :param alarm_name: Nombre de la alarma.
    :return: Detalles de la alarma.
    """
    try:
        response = cloudwatch_client.describe_alarms(AlarmNames=[alarm_name])
        return response['MetricAlarms'][0] if 'MetricAlarms' in response and len(response['MetricAlarms']) > 0 else None
    except ClientError as e:
        print(f"Error al describir la alarma {alarm_name}: {e.response['Error']['Message']}")
        return None

def delete_alarm(alarm_name):
    """
    Elimina una alarma en AWS CloudWatch.
    :param alarm_name: Nombre de la alarma a eliminar.
    :return: Respuesta de la eliminación de la alarma.
    """
    try:
        response = cloudwatch_client.delete_alarms(AlarmNames=[alarm_name])
        return response
    except ClientError as e:
        print(f"Error al eliminar la alarma {alarm_name}: {e.response['Error']['Message']}")
        return None

def list_metrics(namespace=None, metric_name=None, dimensions=None):
    """
    Lista todas las métricas en AWS CloudWatch.
    :param namespace: Espacio de nombres de la métrica.
    :param metric_name: Nombre de la métrica.
    :param dimensions: Dimensiones opcionales de la métrica.
    :return: Lista de métricas.
    """
    try:
        response = cloudwatch_client.list_metrics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions or []
        )
        return response['Metrics']
    except ClientError as e:
        print(f"Error al listar métricas: {e.response['Error']['Message']}")
        return []

def main():
    """
    Método principal que demuestra cómo usar cada función.
    """
    # Parámetros para las funciones
    alarm_name = 'ExampleAlarm'
    metric_name = 'ExampleMetric'
    namespace = 'ExampleNamespace'
    threshold = 50
    comparison_operator = 'GreaterThanOrEqualToThreshold'
    evaluation_periods = 1
    period = 60
    statistic = 'Average'
    value = 60
    dimensions = [{'Name': 'InstanceId', 'Value': 'i-1234567890abcdef0'}]
    
    # Crear una alarma
    print("Creando la alarma...")
    create_response = create_alarm(alarm_name, metric_name, namespace, threshold, comparison_operator, evaluation_periods, period, statistic)
    print("Respuesta de la creación de la alarma:", create_response)
    
    # Publicar datos de métricas
    print("Publicando datos de métricas...")
    put_response = put_metric_data(namespace, metric_name, value, dimensions)
    print("Respuesta de la publicación de datos de métricas:", put_response)
    
    # Obtener estadísticas de métricas
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    print("Obteniendo estadísticas de métricas...")
    stats = get_metric_statistics(namespace, metric_name, start_time, end_time, period, 'Average', dimensions)
    print("Estadísticas de la métrica:", stats)
    
    # Listar alarmas
    print("Listando alarmas...")
    alarms = list_alarms()
    print("Alarmas encontradas:", alarms)
    
    # Describir una alarma
    print("Describiendo la alarma...")
    alarm_details = describe_alarm(alarm_name)
    print("Detalles de la alarma:", alarm_details)
    
    # Eliminar una alarma
    print("Eliminando la alarma...")
    delete_response = delete_alarm(alarm_name)
    print("Respuesta de la eliminación de la alarma:", delete_response)
    
    # Listar métricas
    print("Listando métricas...")
    metrics = list_metrics(namespace)
    print("Métricas encontradas:", metrics)

# Ejecutar la función main si este archivo se ejecuta directamente
if __name__ == "__main__":
    main()

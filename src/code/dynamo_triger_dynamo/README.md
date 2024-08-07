# Integración de DynamoDB Streams, AWS Lambda y AWS Glue

Este documento proporciona una guía detallada para configurar una integración entre DynamoDB Streams, AWS Lambda y AWS Glue. El objetivo es copiar automáticamente los datos de una tabla de DynamoDB a otra cuando se produzcan cambios.

## Tabla de Contenidos

1. [Función Lambda](#1-función-lambda)
2. [Configuración de IAM para Lambda](#2-configuración-de-iam-para-lambda)
3. [Trabajo de AWS Glue](#3-trabajo-de-aws-glue)
4. [Configuración de DynamoDB](#4-configuración-de-dynamodb)
5. [Configuración de Roles y Permisos IAM](#5-configuración-de-roles-y-permisos-iam)
6. [Pruebas](#6-pruebas)
7. [Recursos](#7-recursos)

## 1. Función Lambda

La función Lambda se encarga de escuchar los cambios en los streams de DynamoDB y desencadenar un trabajo en AWS Glue. Aquí está el código y su explicación.

### Código de Lambda (Python)

```python
import boto3
import json

def lambda_handler(event, context):
    # Inicializar el cliente de AWS Glue
    glue_client = boto3.client('glue')

    # Iterar sobre los registros recibidos en el evento de DynamoDB
    for record in event['Records']:
        # Solo manejar eventos de inserción o modificación
        if record['eventName'] in ['INSERT', 'MODIFY']:
            # Extraer la nueva imagen del registro de DynamoDB
            new_image = record['dynamodb']['NewImage']
            print(f"New image: {json.dumps(new_image)}")

            # Intentar iniciar un trabajo de Glue
            try:
                response = glue_client.start_job_run(JobName='TuGlueJobName')
                print(f"Glue job started successfully: {response}")
            except Exception as e:
                # Manejar errores al iniciar el trabajo de Glue
                print(f"Error starting Glue job: {str(e)}")
```

### Explicación del Código

- **boto3.client('glue')**: Crea un cliente de Glue para interactuar con el servicio desde Lambda.
- **event['Records']**: Accede a los registros que el evento de DynamoDB pasa a Lambda.
- **record['eventName']**: Determina el tipo de evento (INSERT o MODIFY) que se ha producido.
- **start_job_run(JobName='TuGlueJobName')**: Inicia un trabajo de Glue específico. Reemplaza `'TuGlueJobName'` con el nombre del trabajo de Glue configurado.

## 2. Configuración de IAM para Lambda

Para que Lambda tenga los permisos necesarios, debes asignarle un rol IAM con las siguientes políticas.

### Políticas de IAM para Lambda

- **AmazonDynamoDBReadOnlyAccess:** Permite a Lambda acceder a los streams de DynamoDB.
- **AWSGlueConsoleFullAccess:** Permite iniciar trabajos de AWS Glue.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:DescribeStream",
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "dynamodb:ListStreams"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/api-pagos/stream/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "glue:StartJobRun"
            ],
            "Resource": "arn:aws:glue:us-east-1:123456789012:job/TuGlueJobName"
        }
    ]
}
```

### Explicación del JSON de Políticas de IAM para Lambda

- **Action:** Lista las acciones permitidas para el rol, como `dynamodb:DescribeStream` para acceder a los streams de DynamoDB.
- **Resource:** Especifica los recursos de AWS a los que se aplican estas acciones. Reemplaza los valores de ARN con los correspondientes a tu cuenta y región.

## 3. Trabajo de AWS Glue

AWS Glue se encargará de copiar los datos desde `api-pagos` a `api-pos-backup`. A continuación, se muestra el script y cómo configurarlo.

### Script de Glue (Python)

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Obtener los argumentos del trabajo de Glue
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Inicializar los contextos de Spark y Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Leer datos desde la tabla DynamoDB de origen
dyf_source = glueContext.create_dynamic_frame.from_catalog(
    database="tu_base_de_datos",
    table_name="api_pagos"
)

# Transformar los datos si es necesario
dyf_transformed = ApplyMapping.apply(
    frame=dyf_source,
    mappings=[
        ("atributo1", "tipo1", "atributo1_destino", "tipo1"),
        ("atributo2", "tipo2", "atributo2_destino", "tipo2"),
    ]
)

# Escribir los datos transformados en la tabla de destino
glueContext.write_dynamic_frame.from_options(
    frame=dyf_transformed,
    connection_type="dynamodb",
    connection_options={
        "dynamodb.output.tableName": "api_pos_backup",
        "dynamodb.throughput.write.percent": "1.0"
    }
)

# Finalizar el trabajo de Glue
job.commit()
```

### Explicación del Script

- **getResolvedOptions:** Obtiene los argumentos de entrada pasados al script.
- **create_dynamic_frame.from_catalog:** Carga datos desde una tabla DynamoDB especificada en el catálogo de Glue.
- **ApplyMapping:** Permite transformar y mapear columnas entre la tabla de origen y la de destino.
- **write_dynamic_frame.from_options:** Escribe los datos transformados en la tabla DynamoDB de destino.

## 4. Configuración de DynamoDB

### Habilitar Streams en `api-pagos`

1. **Acceder a la consola de AWS DynamoDB:**
   - Dirígete a [Consola de DynamoDB](https://console.aws.amazon.com/dynamodb).

2. **Seleccionar la tabla `api-pagos`:**
   - En la pestaña de configuración de la tabla, habilita los streams.

3. **Seleccionar el modo de vista de imágenes:**
   - Elige **New and old images** para capturar imágenes completas de los registros antes y después de los cambios.

### Crear la tabla `api-pos-backup`

1. **En la consola de DynamoDB:**
   - Crea una nueva tabla llamada `api-pos-backup`.

2. **Definir atributos:**
   - Asegúrate de que los atributos coincidan con los definidos en el script de Glue.

## 5. Configuración de Roles y Permisos IAM

### Rol IAM para Glue

El rol IAM para Glue debe tener estas políticas.

#### Políticas de IAM para Glue

- **AmazonDynamoDBFullAccess:** Permite acceso completo a las tablas DynamoDB.
- **AWSGlueServiceRole:** Permite la ejecución de trabajos de Glue.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:DescribeTable",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:123456789012:table/api-pagos",
                "arn:aws:dynamodb:us-east-1:123456789012:table/api-pos-backup"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "glue:CreateJob",
                "glue:DeleteJob",
                "glue:GetJob",
                "glue:GetJobs",
                "glue:StartJobRun",
                "glue:GetJobRun",
                "glue:GetJobRuns"
            ],
            "Resource": "arn:aws:glue:us-east-1:123456789012:job/TuGlueJobName"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

### Explicación del JSON de Políticas de IAM para Glue

- **BatchGetItem, BatchWriteItem, etc.:** Permisos para operaciones de lectura y escritura en DynamoDB.
- **glue:StartJobRun:** Permite iniciar el trabajo de Glue. Asegúrate de reemplazar `arn:aws:glue:us-east-1:123456789012:job/TuGlueJobName` con el ARN de tu trabajo de Glue.
- **s3:GetObject y s3:PutObject:** Permisos para interactuar con

 un bucket de S3 si se utiliza como parte del flujo de trabajo.

## 6. Pruebas

Para asegurarte de que todo está funcionando correctamente:

1. **Probar la función Lambda:**
   - Usa la consola de Lambda para enviar eventos de prueba y verificar que el trabajo de Glue se inicia correctamente.

2. **Verificar los datos en `api-pos-backup`:**
   - Realiza cambios en `api-pagos` y verifica si los datos se copian a `api-pos-backup`.

3. **Revisar logs en CloudWatch:**
   - Revisa los logs de Lambda y Glue en CloudWatch para asegurar que no haya errores.

## 7. Recursos

- [Documentación de AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Documentación de AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Documentación de DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html)
- [Documentación de IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)

---

Espero que este documento te sea útil para tu configuración. Si necesitas más detalles o ajustes, avísame.

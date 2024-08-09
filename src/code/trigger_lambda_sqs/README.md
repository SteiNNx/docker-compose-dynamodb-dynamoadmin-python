# Proyecto: Integración DynamoDB con AWS Lambda y SQS

Este proyecto demuestra cómo integrar Amazon DynamoDB con AWS Lambda y Amazon Simple Queue Service (SQS) para crear un flujo de procesamiento de datos. El flujo involucra insertar datos en una tabla DynamoDB, desencadenar un stream que activa una función Lambda (`unload-rec`), enviar un mensaje a una cola SQS, y finalmente procesar los mensajes acumulados para insertarlos en una tabla réplica de DynamoDB.

## Diagrama de Flujo

```plaintext
+----------------+     +------------------+     +-----------+     +------------------+
|                |     |                  |     |           |     |                  |
|   DynamoDB     +---->+  Lambda (Stream) +---->+    SQS    +---->+ Lambda (Replica) |
|    Table       |     |   unload-rec     |     |  Queue    |     |                  |
|                |     |                  |     |           |     |                  |
+----------------+     +------------------+     +-----------+     +------------------+
```

## Tabla de Pasos

| Paso | Descripción                                                                 |
|------|-----------------------------------------------------------------------------|
| 1    | Insertar datos en la tabla principal de DynamoDB.                           |
| 2    | El stream de DynamoDB activa la función Lambda `unload-rec`.                |
| 3    | La Lambda `unload-rec` envía un mensaje con los datos a la cola SQS.        |
| 4    | Cuando se acumulan 10 mensajes en la cola SQS, la función Lambda los procesa e inserta los datos en la tabla réplica de DynamoDB. |

## Archivos y Código

### 1. Configuración del Entorno

Crea un archivo `.env` con las siguientes variables:

```ini
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_SESSION_TOKEN=your-session-token
AWS_REGION=us-east-1
DYNAMODB_TABLE_PRIMARY=your-primary-table-name
DYNAMODB_TABLE_REPLICA=your-replica-table-name
SQS_QUEUE_URL=your-sqs-queue-url
```

Asegúrate de reemplazar los valores con tus credenciales de AWS y los nombres de tus recursos.

### 2. Código de la Lambda `unload-rec`

Este código procesa eventos de DynamoDB y envía mensajes a SQS.

```python
import json
import boto3
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Constantes
AWS_REGION = os.getenv('AWS_REGION')
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')
EVENT_NAME_INSERT = 'INSERT'
DYNAMODB_NEW_IMAGE = 'NewImage'
DYNAMODB_RECORDS = 'Records'
DYNAMODB_EVENT_NAME = 'eventName'

# Configuración de SQS
sqs = boto3.client('sqs', region_name=AWS_REGION)

def lambda_handler(event, context):
    """
    Handler para procesar eventos de DynamoDB y enviar mensajes a SQS.

    Parámetros:
    - event: dict, evento que contiene registros de cambios en DynamoDB.
    - context: object, información del runtime de Lambda.

    Retorna:
    - dict: con el estado HTTP y un mensaje de resultado.
    """
    try:
        # Iterar sobre cada registro en el evento
        for record in event[DYNAMODB_RECORDS]:
            # Verificar si el evento es una inserción
            if record[DYNAMODB_EVENT_NAME] == EVENT_NAME_INSERT:
                # Obtener la nueva imagen del registro
                new_image = record['dynamodb'][DYNAMODB_NEW_IMAGE]
                message_body = json.dumps(new_image)
                
                # Enviar el mensaje a SQS
                sqs.send_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MessageBody=message_body
                )

        return {
            'statusCode': 200,
            'body': json.dumps('Mensaje enviado a SQS')
        }

    except sqs.exceptions.ClientError as e:
        # Manejar errores específicos de SQS
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error de SQS: {str(e)}')
        }

    except Exception as e:
        # Manejar cualquier otra excepción no esperada
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error procesando el evento: {str(e)}')
        }
```

### 3. Código de la Lambda para Procesar SQS

Este código extrae mensajes de SQS y los inserta en la tabla réplica de DynamoDB.

```python
import json
import boto3
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Constantes
AWS_REGION = os.getenv('AWS_REGION')
DYNAMODB_TABLE_REPLICA = os.getenv('DYNAMODB_TABLE_REPLICA')
RECORDS_KEY = 'Records'
BODY_KEY = 'body'

# Configuración de DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
replica_table = dynamodb.Table(DYNAMODB_TABLE_REPLICA)

def lambda_handler(event, context):
    """
    Handler para procesar eventos de SQS y escribir en una tabla DynamoDB.

    Parámetros:
    - event: dict, evento que contiene registros de mensajes de SQS.
    - context: object, información del runtime de Lambda.

    Retorna:
    - dict: con el estado HTTP y un mensaje de resultado.
    """
    try:
        # Extraer mensajes de los registros del evento
        messages = [json.loads(record[BODY_KEY]) for record in event[RECORDS_KEY]]
        
        # Insertar mensajes en la tabla réplica de DynamoDB
        with replica_table.batch_writer() as batch:
            for message in messages:
                batch.put_item(Item=message)

        return {
            'statusCode': 200,
            'body': json.dumps('Datos insertados en la tabla réplica')
        }

    except dynamodb.meta.client.exceptions.ClientError as e:
        # Manejar errores específicos de DynamoDB
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error de DynamoDB: {str(e)}')
        }

    except Exception as e:
        # Manejar cualquier otra excepción no esperada
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error procesando el evento: {str(e)}')
        }
```

### 4. Políticas IAM

Para garantizar que tus funciones Lambda tengan los permisos necesarios, utiliza las siguientes políticas IAM.

#### Política para `unload-rec`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:REGION:ACCOUNT_ID:QUEUE_NAME"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:DescribeStream",
        "dynamodb:GetRecords",
        "dynamodb:GetShardIterator",
        "dynamodb:ListStreams"
      ],
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/TABLE_NAME/stream/*"
    }
  ]
}
```

#### Política para la Lambda que procesa SQS

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sqs:ReceiveMessage",
      "Resource": "arn:aws:sqs:REGION:ACCOUNT_ID:QUEUE_NAME"
    },
    {
      "Effect": "Allow",
      "Action": "dynamodb:BatchWriteItem",
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/REPLICA_TABLE_NAME"
    }
  ]
}
```

### Advertencias y Consideraciones

- **Tiempos de Espera y Límite de Ejecución**: Asegúrate de configurar adecuadamente los tiempos de espera y límites de ejecución de tus funciones Lambda para manejar la carga esperada de mensajes.
- **Escalabilidad**: Considera la escalabilidad de tus recursos, especialmente SQS y DynamoDB, para manejar picos de tráfico.
- **Seguridad**: Mantén seguras tus credenciales de AWS y limita los permisos IAM a lo estrictamente necesario.

### Recursos Oficiales

- [Documentación de AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Documentación de Amazon SQS](https://docs.aws.amazon.com/sqs/)
- [Documentación de Amazon DynamoDB](https://docs.aws.amazon.com/dynamodb/)

## Configuración Adicional

- **DynamoDB Streams**: Activa los streams en la tabla primaria de DynamoDB para capturar los eventos de inserción.
- **Cola SQS**: Configura una cola SQS con las políticas adecuadas para que las funciones Lambda puedan interactuar con ella.
- **Permisos IAM**: Asegúrate de que las políticas IAM se apliquen correctamente y que las funciones Lambda tengan los permisos necesarios para acceder a los recursos.

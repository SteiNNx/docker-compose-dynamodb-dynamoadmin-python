### 1. Configuración de DynamoDB con TTL (Time-to-Live)

**1.1 Crear la tabla DynamoDB con TTL**

Para habilitar TTL (Time-to-Live) en DynamoDB, necesitas especificar un atributo que actúe como la fecha/hora en que el ítem debe ser eliminado. A continuación, se muestra un ejemplo para crear una tabla con TTL habilitado:

**1.1.1 Crear la tabla (si aún no la tienes):**

```bash
aws dynamodb create-table --table-name api-pos-pago-ttl \
    --attribute-definitions AttributeName=pk,AttributeType=S \
    --key-schema AttributeName=pk,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

**1.1.2 Habilitar TTL en la tabla existente:**

```bash
aws dynamodb update-time-to-live --table-name api-pos-pago-ttl \
    --time-to-live-specification AttributeName=ttl,Enabled=true
```

**Nota:** El atributo `ttl` debe ser un timestamp en formato UNIX epoch que indica cuándo el ítem debe ser eliminado.

### 2. Configuración de Kinesis Data Streams

**2.1 Crear un Stream de Kinesis**

Este stream capturará los eventos de DynamoDB (cuando los ítems sean eliminados).

```bash
aws kinesis create-stream --stream-name api-pos-pago-ttl-stream --shard-count 1
```

**2.2 Configurar DynamoDB Streams para enviar datos a Kinesis**

Primero, asegúrate de que tu tabla DynamoDB esté configurada para enviar eventos a Kinesis. Esto se hace en la consola de DynamoDB o mediante el siguiente comando (esto es opcional si ya tienes configurado el Stream):

```bash
aws dynamodb update-table --table-name api-pos-pago-ttl \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES
```

**2.3 Asociar el stream de DynamoDB con el stream de Kinesis**

Para hacer esto, deberás usar un servicio intermedio como AWS Lambda para procesar los datos de Kinesis y almacenarlos en S3, ya que DynamoDB Streams no envía datos directamente a Kinesis Data Streams.

### 3. Configuración de Lambda Function

**3.1 Crear el código de Lambda**

Aquí tienes un ejemplo de código para la función Lambda que lee de Kinesis y almacena en S3:

**`lambda_function.py`:**

```python
import json
import boto3
import base64
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        # Decodificar el dato de Kinesis
        payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        data = json.loads(payload)
        
        # Crear un nombre único para el archivo en S3
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        s3_key = f"archived_data/{timestamp}.json"
        
        # Subir el dato a S3
        s3.put_object(
            Bucket='your-s3-bucket-name',
            Key=s3_key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data processed successfully')
    }
```

**3.2 Crear la configuración de la función Lambda**

**`lambda_configuration.json`:**

```json
{
  "FunctionName": "archive_to_s3_function",
  "Runtime": "python3.8",
  "Role": "arn:aws:iam::123456789012:role/lambda_basic_execution",
  "Handler": "lambda_function.lambda_handler",
  "Code": {
    "S3Bucket": "your-lambda-code-bucket",
    "S3Key": "lambda_code.zip"
  },
  "Timeout": 60,
  "MemorySize": 128
}
```

**3.3 Desplegar la función Lambda**

```bash
aws lambda create-function --cli-input-json file://lambda_configuration.json
```

**3.4 Configurar el trigger de Kinesis para Lambda**

```bash
aws lambda create-event-source-mapping --function-name archive_to_s3_function \
    --event-source-arn arn:aws:kinesis:region:123456789012:stream/api-pos-pago-ttl-stream \
    --batch-size 100 --starting-position TRIM_HORIZON
```

### 4. Configuración de Permisos en IAM

**4.1 Crear la política de permisos para Lambda**

**`lambda_policy.json`:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::your-s3-bucket-name/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kinesis:GetRecords",
        "kinesis:GetShardIterator",
        "kinesis:DescribeStream",
        "kinesis:ListStreams"
      ],
      "Resource": "arn:aws:kinesis:region:123456789012:stream/api-pos-pago-ttl-stream"
    }
  ]
}
```

**4.2 Adjuntar la política al rol de Lambda**

```bash
aws iam put-role-policy --role-name lambda_basic_execution --policy-name lambda_kinesis_s3_policy --policy-document file://lambda_policy.json
```

### Resumen de Archivos

- `lambda_function.py`: Código de la función Lambda para archivar datos en S3.
- `lambda_configuration.json`: Configuración para crear la función Lambda.
- `lambda_policy.json`: Política de permisos para Lambda.

### Notas Adicionales

1. **Bucket de S3:** Asegúrate de reemplazar `your-s3-bucket-name` con el nombre real de tu bucket en S3.
2. **Bucket de código Lambda:** Reemplaza `your-lambda-code-bucket` con el nombre del bucket donde has subido el código de Lambda (`lambda_code.zip`).
3. **Región y ARN:** Sustituye `region` y `123456789012` con la región AWS y el ID de cuenta correcta en los ARN.

Si necesitas más ayuda o tienes preguntas específicas, no dudes en preguntar.
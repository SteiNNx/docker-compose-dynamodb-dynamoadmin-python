# Guía Completa de IAM (Identity and Access Management) en AWS

Esta guía proporciona una introducción detallada a AWS Identity and Access Management (IAM), explicando conceptos clave, estructuras de políticas, ejemplos prácticos y mejores prácticas.

## Tabla de Contenidos

1. [Introducción a IAM](#1-introducción-a-iam)
2. [Conceptos Básicos](#2-conceptos-básicos)
   - [Políticas IAM](#21-políticas-iam)
   - [Roles IAM](#22-roles-iam)
   - [Usuarios y Grupos IAM](#23-usuarios-y-grupos-iam)
3. [Políticas IAM](#3-políticas-iam)
   - [Estructura de una Política](#31-estructura-de-una-política)
   - [Ejemplos de Políticas](#32-ejemplos-de-políticas)
4. [Roles IAM](#4-roles-iam)
   - [Creación y Asignación de Roles](#41-creación-y-asignación-de-roles)
   - [Ejemplos de Roles](#42-ejemplos-de-roles)
5. [Usuarios y Grupos IAM](#5-usuarios-y-grupos-iam)
   - [Creación de Usuarios](#51-creación-de-usuarios)
   - [Creación de Grupos](#52-creación-de-grupos)
   - [Asignación de Permisos a Grupos](#53-asignación-de-permisos-a-grupos)
6. [Ejemplos de Políticas IAM](#6-ejemplos-de-políticas-iam)
   - [Acceso Completo a un Bucket S3](#61-acceso-completo-a-un-bucket-s3)
   - [Permisos Específicos para DynamoDB](#62-permisos-específicos-para-dynamodb)
   - [Permisos para EC2](#63-permisos-para-ec2)
   - [Permisos para Lambda](#64-permisos-para-lambda)
7. [Mejores Prácticas](#7-mejores-prácticas)
8. [Recursos Adicionales](#8-recursos-adicionales)

---

## 1. Introducción a IAM

AWS Identity and Access Management (IAM) permite gestionar de manera segura el acceso a los recursos de AWS. IAM proporciona la capacidad de controlar quién puede realizar qué acciones en qué recursos dentro de tu cuenta de AWS.

### Funciones Principales

- **Autenticación:** Verifica la identidad de los usuarios que acceden a tus recursos.
- **Autorización:** Define los permisos que los usuarios y servicios tienen sobre los recursos.
- **Auditoría:** Realiza el seguimiento de las acciones realizadas y asegura el cumplimiento de las políticas.

---

## 2. Conceptos Básicos

### 2.1 Políticas IAM

Las políticas IAM son documentos en formato JSON que definen los permisos de acceso. Estas políticas se pueden asignar a usuarios, grupos o roles y especifican qué acciones están permitidas o denegadas para los recursos especificados.

#### Componentes de una Política

- **Version:** La versión del lenguaje de políticas (por ejemplo, "2012-10-17").
- **Statement:** Una o más declaraciones que definen los permisos.

Cada declaración incluye:

- **Effect:** `Allow` o `Deny`.
- **Action:** Las acciones permitidas o denegadas (por ejemplo, `s3:ListBucket`).
- **Resource:** Los recursos sobre los cuales se aplican las acciones (por ejemplo, `arn:aws:s3:::mi-bucket`).

### 2.2 Roles IAM

Los roles IAM permiten a los servicios y usuarios asumir permisos específicos sin necesidad de crear credenciales individuales. Los roles se utilizan para delegar permisos a servicios, aplicaciones y usuarios.

#### Componentes de un Rol

- **Trust Policy:** Define quién puede asumir el rol.
- **Permissions Policy:** Define los permisos que el rol otorga.

### 2.3 Usuarios y Grupos IAM

- **Usuarios:** Entidades individuales que representan una identidad dentro de la cuenta.
- **Grupos:** Colecciones de usuarios que comparten permisos comunes. Los permisos se aplican a todos los miembros del grupo.

---

## 3. Políticas IAM

### 3.1 Estructura de una Política

Una política IAM se define en JSON y puede tener una estructura básica como la siguiente:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "service:Action",
            "Resource": "arn:aws:service:region:account-id:resource"
        }
    ]
}
```

### 3.2 Ejemplos de Políticas

#### Acceso Básico a un Bucket S3

Permite listar objetos en un bucket específico de S3.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::mi-bucket"
        }
    ]
}
```

#### Acceso Completo a un Bucket S3

Permite todas las acciones sobre un bucket y sus objetos.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::mi-bucket",
                "arn:aws:s3:::mi-bucket/*"
            ]
        }
    ]
}
```

#### Permisos para DynamoDB

Permite realizar operaciones de lectura y escritura en una tabla específica de DynamoDB.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/mi-tabla"
        }
    ]
}
```

#### Permisos para EC2

Permite iniciar, detener y reiniciar instancias EC2.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:RebootInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## 4. Roles IAM

### 4.1 Creación y Asignación de Roles

Para crear un rol en IAM:

1. **Ir a la consola de IAM:** [Consola IAM](https://console.aws.amazon.com/iam)
2. **Seleccionar "Roles"** y hacer clic en "Crear rol".
3. **Elegir un tipo de entidad confiable:** Seleccionar AWS Service, IAM User, o otra entidad.
4. **Asignar permisos al rol:** Seleccionar una política o crear una nueva.
5. **Asignar etiquetas (opcional):** Etiqueta el rol para facilitar la gestión.
6. **Revisar y crear el rol.**

### 4.2 Ejemplos de Roles

#### Rol para Lambda

Permite a una función Lambda escribir logs en CloudWatch y acceder a DynamoDB.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:Scan",
            "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/mi-tabla"
        }
    ]
}
```

#### Rol para EC2 con Acceso a S3

Permite a una instancia EC2 acceder a un bucket específico de S3.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::mi-bucket",
                "arn:aws:s3:::mi-bucket/*"
            ]
        }
    ]
}
```

---

## 5. Usuarios y Grupos IAM

### 5.1 Creación de Usuarios

Para crear un usuario IAM:

1. **Ir a la consola de IAM:** [Consola IAM](https://console.aws.amazon.com/iam)
2. **Seleccionar "Usuarios"** y hacer clic en "Agregar usuario".
3. **Definir un nombre de usuario** y seleccionar el tipo de acceso (programático o a la consola).
4. **Asignar permisos:** Directamente o mediante un grupo.
5. **Configurar la opción de MFA (opcional):** Configurar la autenticación multifactor para mayor seguridad.
6. **Revisar y crear el usuario.**

### 5.2 Creación de Grupos

Para crear un grupo IAM:

1. **Ir a la consola de IAM:** [Consola

 IAM](<https://console.aws.amazon.com/iam>)
2. **Seleccionar "Grupos"** y hacer clic en "Crear grupo".
3. **Asignar políticas:** Seleccionar políticas predefinidas o crear nuevas.
4. **Agregar usuarios al grupo.**

### 5.3 Asignación de Permisos a Grupos

Para asignar permisos a un grupo:

1. **Seleccionar el grupo en la consola de IAM.**
2. **Ir a la pestaña "Permisos".**
3. **Agregar políticas:** Seleccionar políticas predefinidas o crear nuevas.

---

Claro, aquí tienes una serie de ejemplos de políticas IAM para diferentes servicios y escenarios comunes en AWS. Cada política está diseñada para abordar casos específicos y proporcionar una visión de cómo configurar permisos de forma granular.

---

## 6. Ejemplos de Políticas IAM

### 6.1 Acceso Completo a un Bucket S3

Permite realizar todas las operaciones en un bucket específico y en sus objetos.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::mi-bucket",
                "arn:aws:s3:::mi-bucket/*"
            ]
        }
    ]
}
```

### 6.2 Permisos Específicos para DynamoDB

Permite realizar operaciones de lectura y escritura en una tabla de DynamoDB.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/mi-tabla"
        }
    ]
}
```

### 6.3 Permisos para EC2

Permite iniciar, detener y describir instancias EC2.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:RebootInstances",
                "ec2:DescribeInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

### 6.4 Permisos para Lambda

Permite invocar funciones Lambda y escribir en logs.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction",
                "lambda:ListFunctions"
            ],
            "Resource": "arn:aws:lambda:us-east-1:123456789012:function:mi-funcion-lambda"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

### 6.5 Acceso a RDS

Permite realizar operaciones de administración en una base de datos RDS específica.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rds:DescribeDBInstances",
                "rds:RebootDBInstance",
                "rds:StopDBInstance",
                "rds:StartDBInstance"
            ],
            "Resource": "arn:aws:rds:us-east-1:123456789012:db:mi-db-instance"
        }
    ]
}
```

### 6.6 Acceso a SNS

Permite publicar y suscribirse a un tema SNS.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish",
                "sns:Subscribe",
                "sns:ListSubscriptions",
                "sns:ListSubscriptionsByTopic"
            ],
            "Resource": "arn:aws:sns:us-east-1:123456789012:mi-tema"
        }
    ]
}
```

### 6.7 Permisos para CloudWatch Logs

Permite administrar y visualizar logs en CloudWatch.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:GetLogEvents",
                "logs:CreateLogGroup",
                "logs:CreateLogStream"
            ],
            "Resource": "*"
        }
    ]
}
```

### 6.8 Permisos para IAM

Permite administrar usuarios, grupos y roles IAM.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateUser",
                "iam:DeleteUser",
                "iam:UpdateUser",
                "iam:CreateGroup",
                "iam:DeleteGroup",
                "iam:UpdateGroup",
                "iam:AttachUserPolicy",
                "iam:DetachUserPolicy",
                "iam:AttachGroupPolicy",
                "iam:DetachGroupPolicy"
            ],
            "Resource": "*"
        }
    ]
}
```

### 6.9 Permisos para ECR (Elastic Container Registry)

Permite administrar imágenes en un repositorio de ECR.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage"
            ],
            "Resource": "arn:aws:ecr:us-east-1:123456789012:repository/mi-repositorio"
        }
    ]
}
```

### 6.10 Permisos para SQS

Permite enviar y recibir mensajes desde una cola SQS.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:ListQueues"
            ],
            "Resource": "arn:aws:sqs:us-east-1:123456789012:mi-cola"
        }
    ]
}
```

### 6.11 Permisos para KMS (Key Management Service)

Permite gestionar y utilizar claves de cifrado en KMS.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:GenerateDataKey",
                "kms:DescribeKey",
                "kms:ListAliases"
            ],
            "Resource": "arn:aws:kms:us-east-1:123456789012:key/mi-clave"
        }
    ]
}
```

### 6.12 Permisos para CloudFormation

Permite crear, actualizar y eliminar stacks en CloudFormation.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateStack",
                "cloudformation:UpdateStack",
                "cloudformation:DeleteStack",
                "cloudformation:DescribeStackResources",
                "cloudformation:ListStackResources"
            ],
            "Resource": "*"
        }
    ]
}
```

### 6.13 Permisos para Route 53

Permite gestionar registros de DNS en Route 53.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "route53:ListHostedZones",
                "route53:GetHostedZone",
                "route53:ChangeResourceRecordSets"
            ],
            "Resource": "*"
        }
    ]
}
```

### 6.14 Permisos para S3 con Restricción por IP

Permite acceso a un bucket S3 solo desde una IP específica.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::mi-bucket",
                "arn:aws:s3:::mi-bucket/*"
            ],
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "203.0.113.0/24"
                }
            }
        }
    ]
}
```

### 6.15 Permisos para Auto Scaling

Permite gestionar configuraciones y políticas de Auto Scaling.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "autoscaling:CreateAutoScalingGroup",
                "autoscaling:UpdateAutoScalingGroup",
                "autoscaling:DeleteAutoScalingGroup",
                "autoscaling:DescribeAutoScalingGroups",
                "autoscaling:CreateLaunchConfiguration",
                "autoscaling:UpdateLaunchConfiguration",
                "autoscaling:DeleteLaunchConfiguration"
            ],
            "Resource": "*"
        }
    ]
}
```

### 6.16 Permisos para Step Functions

Permite gestionar flujos de trabajo en AWS Step Functions.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "states:CreateStateMachine",
                "

states:UpdateStateMachine",
                "states:DeleteStateMachine",
                "states:DescribeStateMachine",
                "states:ListStateMachines"
            ],
            "Resource": "arn:aws:states:us-east-1:123456789012:stateMachine:mi-flujo-de-trabajo"
        }
    ]
}
```

## 7. Mejores Prácticas

- **Principio de Menor Privilegio:** Asigna solo los permisos necesarios para realizar una tarea específica.
- **Uso de Roles en Lugar de Credenciales de Usuario:** Utiliza roles para servicios y aplicaciones para evitar el uso de credenciales estáticas.
- **Políticas de Control de Servicio (SCP):** Utiliza SCP con AWS Organizations para aplicar controles a nivel de organización.
- **Auditoría Regular:** Revisa periódicamente las políticas y permisos para asegurar que se alineen con las necesidades actuales.
- **Configuración de MFA:** Implementa la autenticación multifactor (MFA) para usuarios y roles que requieran acceso elevado.

---

## 8. Recursos Adicionales

- [Documentación Oficial de IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)
- [Políticas IAM y Ejemplos](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)
- [Roles IAM para Servicios de AWS](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)
- [Mejores Prácticas de IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

---

Este README proporciona una visión general completa sobre IAM en AWS, desde la definición de políticas hasta la gestión de usuarios y roles. Para configuraciones avanzadas y personalizadas, revisa la documentación oficial y ajusta las políticas según las necesidades específicas de tu organización.

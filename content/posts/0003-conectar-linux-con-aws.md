---
title: "Conectando GNU/Linux con AWS"
slug: conectar-linux-con-aws
authors:
  - tangelov
date: 2018-02-18T11:30:00+02:00
tags:  ["aws", "cloud"]
categories: ["cloud"]
draft: false
---

Amazon fue una de las pioneras de la nube y lanzó Amazon Web Services en el 2006 siendo actualmente la lider del sector. En este artículo vamos a mostrar como podemos interactuar a través del a CLI contra dicha nube.

A diferencia de otros proveedores que tienen herramientas diferenciadas, AWS ofrece una CLI para todos sus servicios llamada AWS CLI. A través de ella podemos acceder al sistema de ECS (máquinas virutales), RDS (bases de datos en PaaS) y otros.

<!--more-->

## Amazon Web Services CLI
La interfaz de línea de comandos de AWS es muy fácil de instalar:

* Si utilizamos Windows, Amazon provee instaladores para sistemas operativos de 64 o 32 bits. También podemos instalarlo en el WLS de Windows 10

* Si utilizamos Linux o Mac, necesitamos tener instalado python en una versión similar o superior a 2.7 o 3.4 en el caso de usar python3.

Si vamos a instalarlo a través de pip tan sólo tenemos que ejecutar este comando:
```bash
pip3 install awscli --user
```

## Configuración
Una vez hemos instalado la herramienta debemos configurarla para acceder a nuestros recursos dentro de AWS.

En primer lugar debemos obtener dos datos del portal de AWS:

* AWS Access Key ID

* AWS Secret Access Key

Para ello, nos vamos a la consola de IAM de AWS y hacemos click en Usuarios, dentro de la pestaña _Security credentials_ podremos crear una Access Key. Podremos generar un fichero .csv con ellos que debemos almacenar en un lugar seguro.

![Generando las claves de AWS](https://storage.googleapis.com/tangelov-data/images/0003-00.png)

Debemos utilizar el comando `aws configure` y completar los datos que se nos piden:

* __AWS Access Key ID__: La parte pública de la clave (en el CSV la primera parte)

* __AWS Secret Access Key__: La parte privada de la clave (en el CSV es la segunda parte tras la coma)

* __Default region name__: Es el sitio donde queremos desplegar las máquinas por defecto (en mi caso estoy usando _eu-west-3_)

* __Default output format__: Elegimos el formato de salida de la consola (uso json)

```bash
aws configure
AWS Access Key ID [None]: NANANANANANAANANANA
AWS Secret Access Key [None]: BAAAAAAAAAAAATMAAAAAAAAAAAAAAAAAAN
Default region name [None]: eu-west-3
Default output format [None]: json
```

Ahora podemos lanzar `aws ec2 describe-instances` para ver todas las instancias que tenemos en dicha zona en formato JSON
```json
{
    "Reservations": [
        {
            "Instances": [
                {
                    "Monitoring": {
                        "State": "disabled"
                    },
                    "PublicDnsName": "",
                    "StateReason": {
                        "Message": "Client.UserInitiatedShutdown: User initiated shutdown",
                        "Code": "Client.UserInitiatedShutdown"
                    },
                    "State": {
                        "Code": 48,
                        "Name": "terminated"
                    },
                    "EbsOptimized": false,
                    "LaunchTime": "2017-01-03T18:55:12.000Z",
                    "ProductCodes": [],
                    "StateTransitionReason": "User initiated (2017-01-03 21:52:55 GMT)",
                    "InstanceId": "batman",
                    "EnaSupport": false,
                    "ImageId": "spiderman",
                    "PrivateDnsName": "",
                    "KeyName": "LaMasa",
                    "SecurityGroups": [],
                    "ClientToken": "DoctorDoom",
                    "InstanceType": "t2.micro",
                    "NetworkInterfaces": [],
                    "Placement": {
                        "Tenancy": "default",
                        "GroupName": "",
                        "AvailabilityZone": "eu-west-3c"
                    },
                    "Hypervisor": "xen",
                    "BlockDeviceMappings": [],
                    "Architecture": "x86_64",
                    "RootDeviceType": "ebs",
                    "RootDeviceName": "/dev/sda1",
                    "VirtualizationType": "hvm",
                    "Tags": [
                        {
                            "Value": "VMPOC01",
                            "Key": "Name"
                        }
                    ],
                    "AmiLaunchIndex": 0
                }
            ],
            "ReservationId": "007",
            "Groups": [],
            "OwnerId": "StanLee"
        },
```

## Documentación

* [Instalación de AWS CLI](https://aws.amazon.com/es/cli/)

* [Repositorio de awscli en Pypi.org (ENG)](https://pypi.org/project/awscli/)

* [First steps in AWS CLI (ENG)](https://docs.aws.amazon.com/es_es/cli/latest/userguide/cli-chap-getting-started.html)

Revisado a 01/03/2021.

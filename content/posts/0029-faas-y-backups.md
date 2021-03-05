---
title: "Funciones y backups: notificaciones y automatismos"
slug: funciones-y-backups
authors:
  - tangelov
date: 2020-03-23T22:00:00+02:00
tags:  ["devops", "functions", "faas", "notificaciones"]
categories: ["devops", "cloud"]
draft: false
---

Una de mis mayores preocupaciones _informáticas_ es la pérdida de datos. Nunca he tenido una pérdida catastrófica pero sí algunas menores y siempre he buscado que mi sistema de respaldo fuese consistente y fiable. Como ya dije [en un post anterior](https://tangelov.me/posts/mi-nube-privada.html), hace tiempo que me monté un sistema de backups personalizado y que me permite recuperar mis datos con una pérdida máxima de datos de 24 horas.

Los backups se generan cifrados con GPG en el origen a través de _Backupninja_ y se suben a almacenamientos en la nube gracias a _rclone_. Se realiza un sistema
 de archivado en MEGA.

![sistema-backups](https://storage.googleapis.com/tangelov-data/images/0029-00.png)


Aunque generalmente funcione bien, sí he tenido algunas incidencias desde que lo implementé, todas ellas relacionadas con la imposibilidad de subir el backup al destino remoto (tokens expirados, discos remotos llenos, etc).

<!--more-->

## Introducción
Debido a lo anterior, estuve pensando cómo recibir un sistema de notificaciones. Lo primero que pensé fue el medio de envío: es fácil enviar correos electrónicos, pero no le hago mucho caso al email y en mi caso prefiero que los mensajes se mandasen a mi cuenta de [Matrix](https://matrix.org/). Matrix es un sistema de mensajería, descentralizado y de código abierto que estoy utilizando y que os recomiendo que le echéis un vistazo ;) .

También pensé que mi sistema de mensajería debía de tener las siguientes características:

* Desacoplar el envío de mensajes y la recepción de los mismos utilizando colas. Así no se pierden y garantizo la entrega de los mensajes.

* Se debían de ejecutar sin intervención humana.

* Deben ejecutarse en sistemas sin operaciones, totalmente gestionados en la nube y dentro del _Free Tier_ de algún proveedor.

Y... me puse manos a la obra.


## Infraestructura
Cualquier proveedor de nube ofrece los servicios necesarios para generar mi sistema, pero Google Cloud era el que tenía más a mano y es el que voy a usar. Estos son los servicios que voy a utilizar:

* __Cloud Scheduler__: es un servicio de _cron_ en la nube que me permite ejecutar ciertas acciones de forma programada y que me va a permitir comprobar una vez al día el estado de mis backups.

* __Cloud Pub/Sub__: Es el servicio de colas global, con el patron Publisher-Subscriber y totalmente gestionado por Google. Es donde vamos a almacenar y a distribuir los distintos mensajes de cada una de las piezas del sistema.

* __Cloud Functions__: Es el servicio de FaaS o _Functions as a Service_ de Google Cloud y permite ejecutar piezas de código que responden automáticamente a eventos. Van a ser las encargadas de procesar los mensajes.

* __Cloud Storage__: Es el servicio de almacenamiento de objetos de GCP (ya hemos hablado alguna vez de él). Vamos a utilizarlo para almacenar los ficheros que necesite todo el sistema.

Más o menos el sistema sería así a alto nivel:

![sistema-notificaciones](https://storage.googleapis.com/tangelov-data/images/0029-01.png)

1 - Cloud Scheduler crea de forma programática un mensaje en un topic de PubSub que contiene un payload que identifica su origen.

2 - La creación de éste mensaje genera un evento que hace que una _Cloud Function_ se ejecute.

3 - Dicha función (_backup checker_)  se conecta a la API de Google Drive, comprueba el estado de los backups del día anterior y si éste no es correcto, genera un mensaje en otro topic de PubSub.

4 - Esta nueva función (_message sender_), recibe el mensaje creado en el segundo topic de PubSub y lo envía a una sala de Matrix, donde lo recibo en alguno de mis dispositivos personales.

5 - El servicio es extensible. Si necesito que lleguen nuevas notificaciones de cualquier tipo, tan sólo tengo que ingresar mensajes en la segunda cola de PubSub y éstas se enviarán sin demora.

__EXTRA__: Todas las dependencias se encuentran almacenadas en un bucket de Cloud Storage.

Todos estos elementos, salvo las funciones, están terraformados. Si alguien quiere revisar el código, puede consultarse [aquí](https://gitlab.com/tangelov/tangelov-infra/-/tree/ed040ffe65b25f23778b3725bd7734fb8cccc971), principalmente en las carpetas de _IAM_ y _PubSub_.

Por ejemplo, éste sería el código para crear un job de _Cloud Scheduler_:

```bash
resource "google_cloud_scheduler_job" "cscheduler_backups" {
  name        = var.cscheduler_backup_checker_name
  description = var.cscheduler_backup_checker_description
  schedule    = var.cscheduler_backup_checker_cron
  time_zone   = var.cscheduler_backup_checker_timezone

  region = var.gcp_app_engine_location

  pubsub_target {
    topic_name = $IDENTIFICADOR_DEL_TOPIC_DE_PUBSUB
    data       = base64encode(var.cscheduler_backup_checker_payload)
  }
}
``` 

> Cloud Scheduler se despliega en la misma región en la que lo haga Google App Engine por limitaciones del proveedor. Si actualmente no estamos utilizando el App Engine, ésto podría limitarnos en el futuro por lo que hay que tener cuidado.

Junto a los elementos más evidentes también es necesario _terraformar_ los elementos que permiten a las Cloud Functions hacer sus tareas, como los permisos de IAM en topics de PubSub o buckets de Google Cloud Storage.

Esta sería la estructura que tendría cada función:

![estructura-funcion](https://storage.googleapis.com/tangelov-data/images/0029-02.png)

Con Terraform también podemos crear permisos. Así crearíamos una cuenta de servicio, un topic de PubSub y los permisos para poder operar con él:

```bash
# Cuenta de servicio para acceder a Pub Sub
resource "google_service_account" "gcp_functions_sa" {
  account_id   = var.sa_functions_account_id
  display_name = var.sa_functions_display_name
  description  = var.sa_functions_description

  project = var.gcp_default_project
}

# Topic en Google Cloud PubSub para las notificaciones
resource "google_pubsub_topic" "matrix-notifications" {
  name = var.matrix_notifications_topic_name

  project = var.gcp_default_project
}

# Permisos para ingestar mensajes en nuestro topic de PubSub
resource "google_pubsub_topic_iam_member" "matrix-not-publisher-iam" {
  topic  = google_pubsub_topic.matrix-notifications.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.gcp_functions_sa.email}"

  project = var.gcp_default_project

  depends_on = [google_service_account.gcp_functions_sa, google_pubsub_topic.matrix-notifications]
}
```

Si utilizamos esta cuenta en nuestra función, podríamos acceder inyectar mensajes en un topic de PubSub sin problemas.

## Cloud functions
El nombre de este post es _Funciones y backups_: una vez ya tenemos toda la infraestructura necesaria, vamos a picar el código que va a poner en marcha el sistema: las funciones. Cada función es un fragmento de código que es ejecutado ante un evento. Si utilizamos un servicio de funciones en la nube, pagamos por el número de ejecuciones y eliminamos toda la gestión de la infraestructura subyacente.

Cloud Functions soporta diferentes lenguajes (Go 1.11/1.13, Python 3.7 o Node.js 8 o 10), pero debido a que desconozco Node.js o Go, vamos a utilizar Python 3.

Recordando el primer esquema, he creado dos funciones diferentes:

* La primera va a encargarse de comprobar que el estado de los backups es el correcto.

* La segunda se va a encargar de recoger un mensaje y enviarlo a través de Matrix a uno de mis dispositivos personales. Vamos a explicar las funciones:

Todas las funciones tienen que tener dos ficheros obligatorios: un _main.py_ con el código y un fichero _requirements.txt_ con las dependencias necesarias para funcionar.

> Si tenemos las funciones almacenadas en un repositorio y deseamos que sólo se suban los ficheros main.py y requirements.txt, podemos generar un fichero llamado .gcloudignore, que funciona como .gitignore, pero para ciertos comandos de la CLI de Google Cloud.

> Si deseamos ver que ficheros van a subirse podemos utilizar el comando ```gcloud meta list-files-for-upload```

### Backup checker
La primera de las funciones coge los mensajes generados por Cloud Scheduler y realiza las comprobaciones contra Google Drive para asegurar el buen estado de los backups. El código de la función puede consultarse [aquí](https://gitlab.com/tangelov-functions/checking-drive-backups).

_Backup checker_ consta de dos partes:

* Una función que comprueba el estado de los backups.

* Otra función secundaria que genera un mensaje en una nueva cola de PubSub con el estado de nuestros backups.

Vamos a proceder a desplegar la primera función:

```bash
# Ejecutamos el siguiente comando
gcloud functions deploy checking_backups \
--runtime python37 \
--trigger-topic $UN_TOPIC_DE_PUBSUB \
--region europe-west1 \
--set-env-vars=GCS_BUCKET=$UN_BUCKET_MOLON,GCP_PUBSUB_TOPIC=matrix-"projects/$PROYECTO/topics/$OTRO_TOPIC_DE_PUBSUB" \
--service-account=$EMAIL_DE_LA_CUENTA_DE_SERVICIO_CON_PERMISOS

# Nos preguntará si queremos permitir invocaciones anónimas a la función
Allow unauthenticated invocations of new function [checking_backups]? 
(y/N)?  N

WARNING: Function created with limited-access IAM policy. To enable unauthorized access consider "gcloud alpha functions add-iam-policy-binding checking_backups --region=europe-west1 --member=allUsers --role=roles/cloudfunctions.invoker"
```

Con esto ya tendremos desplegada nuestra primera función.

### Message sender
La segunda función coge los mensajes generados por la primera función y los procesa para enviarlos a través de Matrix. El código de la función puede consultarse [aquí](https://gitlab.com/tangelov-functions/messages-to-matrix) y está dividida en dos:

* La primera función recoge el mensaje de la cola de PubSub y lo prepara para mandarlo a una sala de Matrix.

```python37
def messages_to_matrix(pubsub_message, context):
    """ This function get the message from the PubSub topic and parse the data
    to send it via Matrix
    """

    # We import base64 library to decode the information
    # inside a PubSub message
    import base64

    # If there is data in the pubsub_message we send it via
    # send_message function
    if 'data' in pubsub_message:
        message = base64.b64decode(pubsub_message['data']).decode('utf-8')
        asyncio.get_event_loop().run_until_complete(send_message(message))
```

<br />

* La segunda función, es una función asíncrona que recoge el mensaje que le ha pasado la primera función y lo envía a una sala de Matrix. Utiliza Matrix Nio, una librería que permite crear clientes de Matrix en Python y que ofrece más garantías que el SDK oficial.

```python37
async def send_message(message):
    """ This async function will get the configuration to connect to
    Matrix and send a message to a Matrix room.
    """

    # Recovering configuration to connect to Matrix account
    client = storage.Client()
    bucket = client.get_bucket(GCS_BUCKET)
    blob = storage.Blob('config.json', bucket)

    # Checking if the blob already exists
    if blob.exists():
        with open('/tmp/config.json', 'wb') as config_file:
            client.download_blob_to_file(blob, config_file)

    # Loading configuration as JSON config file
    with open('/tmp/config.json') as config_data_file:
        config = json.load(config_data_file)

    # Parsing configuration to create the session into a Matrix server
    server = "https://%s" % config['server']
    user = "%s:%s" % (config['user'], config['server'])
    room = "%s:%s" % (config['room'], config['server'])

    # Defining user, server and password to use with Matrix account
    client = AsyncClient(server, user)
    await client.login(config['password'])

    # Sending the message to a Matrix room
    await client.room_send(
        room_id=room,
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": "%s" % message
        }
    )
    # Closing the connection
    await client.close()
```

Si os fijais, la funcionalidad está desacoplada de la recepción de los mensajes. Esto permite que si un día deseo cambiar Matrix por Telegram (por ejemplo) como destino, pueda hacerlo de una forma sencilla.

Vamos a proceder a desplegar la segunda función:

```bash
gcloud functions deploy messages_to_matrix \
--runtime python37 \
--trigger-topic $OTRO_TOPIC_DE_PUBSUB \
--region europe-west1 \
--set-env-vars=GCS_BUCKET=$UN_BUCKET_MOLON \
--service-account=$EMAIL_DE_LA_CUENTA_DE_SERVICIO_CON_PERMISOS
```

Si ahora que hemos desplegado las dos funciones, nos vamos al panel de Google cloud, podemos ver ambas funciones :

![consola-funciones](https://storage.googleapis.com/tangelov-data/images/0029-03.png)

En la consola, también podemos ver sus logs, ver el código fuente o incluso probarla (son los tres botones marcados en la siguiente imágen):

![consola-opciones](https://storage.googleapis.com/tangelov-data/images/0029-04.png)

Y ya está :D . Con ésto ya tendríamos el sistema funcionando. He borrado un par de backups a modo de prueba y ahora los mensajes llegan a mi sala de Matrix sin ningún problema.

![ejemplo-matrix](https://storage.googleapis.com/tangelov-data/images/0029-05.png)

Espero que os haya gustado el post y... ¡nos vemos en el siguiente!

## Documentación

* [Página oficial de Matrix (ENG)](https://matrix.org/)

* [Patrón Publicador-Subscriptor en la Wikipedia en inglés (ENG)](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)

* Documentación oficial de los servicios de GCP utilizados (ENG): [Cloud Scheduler](https://cloud.google.com/scheduler/docs), [Cloud PubSub](https://cloud.google.com/pubsub/docs/quickstart-py-mac), [Cloud Functions](https://cloud.google.com/functions/docs) y [Cloud Storage](https://cloud.google.com/storage/docs)

* [Diferentes formas de acceder a Google Drive (ENG)](https://help.talend.com/reader/E3i03eb7IpvsigwC58fxQg/bS8nwiwx2K9oNXaaFDkokw)

* [Documentación de Matrix Nio (ENG)](https://matrix-nio.readthedocs.io/en/latest/nio.html#asyncclient)

Revisado a 01-03-2021

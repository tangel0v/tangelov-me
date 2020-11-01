---
title: "Conectando Google Cloud Platform (GCP) con Linux"
authors:
  - tangelov
date: 2018-02-18T10:00:00+02:00
tags:  ["gcp", "cloud"]
categories: ["cloud"]
draft: false
---

Google Cloud Platform es la plataforma de nube pública de Google y al igual que Azure o AWS tiene métodos para conectar nuestros ordenadores con ella y trabajar directamente a través de una CLI.

La plataforma de Google Cloud consta por defecto de tres herramientas integradas dentro del SDK de Google Cloud:

* _gcloud_: se usa para interacionar con toda la nube de Google (máquinas virtuales, contenedores, PaaS variados, etc.)

* _gsutil_: se usa para interaccionar con todo lo relacionado con almacenamiento de ficheros en Cloud Storage.

* _bq_: se usa para interaccionar con Big Query (su PaaS de _data warehouse_)

Para tener acceso a dichas herramientas no tenemos más que instalar el SDK de Google Cloud. Está escrito en python, por lo que si queremos realizar algún desarrollo para esta nube, es el lenguaje más adecuado al implementarse cualquier mejora primero aquí.

<!--more-->

## Google Cloud CLI
Tan sólo tenemos que ejecutar los siguientes comandos
```bash
# Descargamos el script que instala el SDK de Google Cloud
curl https://sdk.cloud.google.com | bash

# Y reiniciamos la shell para que coja los cambios
exec -l $SHELL
```

También podemos instalarlo a través de sus repositorios oficiales para [Ubuntu/Debian](https://cloud.google.com/sdk/docs/downloads-apt-get) o para distribuciones basadas en [RPM](https://cloud.google.com/sdk/docs/downloads-yum).

### Configuración
Una vez ya hemos instalado la CLI, debemos iniciarla con
```bash
# Iniciamos el asistente de configuración de Google Cloud SDK
gcloud init --console-only
```
Nos aparecerá una URL que debemos copiar y pegar en un navegador:

![Configuracion de Google Cloud](https://storage.googleapis.com/tangelov-data/images/0002-00.png)

Después debemos loguearnos en nuestra cuenta:

![Login con una cuenta de Google](https://storage.googleapis.com/tangelov-data/images/0002-01.png)

Y pegar el código resultante en la terminal.

Con esto ya estará configurado y si hacemos _gcloud config list_ podremos verla:

![Ejemplo de configuración](https://storage.googleapis.com/tangelov-data/images/0002-02.png)

Nuestra configuración se encuentra en una carpeta dentro de nuestro $HOME llamada _.config/.gcloud_:
```bash
.config
└── gcloud
    ├── access_tokens.db
    ├── active_config
    ├── config_sentinel
    ├── configurations
    │   └── config_default
    ├── credentials.db
    ├── gce
    ├── legacy_credentials
    │   └── xxxxxxxxxxxx@gmail.com
    │       └── adc.json
    └── logs
        └── 2018.01.15
            ├── 08.20.41.087858.log
            ├── 08.22.18.582898.log
            ├── 09.00.00.155198.log
            ├── 11.09.17.704774.log
            └── 11.09.27.810942.log
```

### Configuración extra
Si necesitamos alguno de los clientes extra que tiene Google Cloud como, por ejemplo, el usado por Big Table, debemos instalarlo. Para ello debemos usar el comando _gcloud components install $nombrecomponente_

También podemos ver todos los componentes disponibles con _gcloud components list_ :

```bash
Your current Cloud SDK version is: 275.0.0
The latest available version is: 275.0.0

┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                  Components                                                 │
├───────────────┬──────────────────────────────────────────────────────┬──────────────────────────┬───────────┤
│     Status    │                         Name                         │            ID            │    Size   │
├───────────────┼──────────────────────────────────────────────────────┼──────────────────────────┼───────────┤
│ Not Installed │ App Engine Go Extensions                             │ app-engine-go            │  56.6 MiB │
│ Not Installed │ Cloud Bigtable Command Line Tool                     │ cbt                      │   6.4 MiB │
│ Not Installed │ Cloud Bigtable Emulator                              │ bigtable                 │   4.3 MiB │
│ Not Installed │ Cloud Datalab Command Line Tool                      │ datalab                  │   < 1 MiB │
│ Not Installed │ Cloud Datastore Emulator                             │ cloud-datastore-emulator │  17.7 MiB │
│ Not Installed │ Cloud Datastore Emulator (Legacy)                    │ gcd-emulator             │  38.1 MiB │
│ Not Installed │ Cloud Firestore Emulator                             │ cloud-firestore-emulator │  27.5 MiB │
│ Not Installed │ Cloud Pub/Sub Emulator                               │ pubsub-emulator          │  33.4 MiB │
│ Not Installed │ Cloud SQL Proxy                                      │ cloud_sql_proxy          │   3.8 MiB │
│ Not Installed │ Emulator Reverse Proxy                               │ emulator-reverse-proxy   │  14.5 MiB │
│ Not Installed │ Google Cloud Build Local Builder                     │ cloud-build-local        │   6.0 MiB │
│ Not Installed │ Google Container Registry's Docker credential helper │ docker-credential-gcr    │   1.8 MiB │
│ Not Installed │ gcloud Alpha Commands                                │ alpha                    │   < 1 MiB │
│ Not Installed │ gcloud Beta Commands                                 │ beta                     │   < 1 MiB │
│ Not Installed │ gcloud app Java Extensions                           │ app-engine-java          │ 108.8 MiB │
│ Not Installed │ gcloud app PHP Extensions                            │ app-engine-php           │           │
│ Not Installed │ gcloud app Python Extensions                         │ app-engine-python        │   6.2 MiB │
│ Not Installed │ gcloud app Python Extensions (Extra Libraries)       │ app-engine-python-extras │  28.5 MiB │
│ Not Installed │ kubectl                                              │ kubectl                  │   < 1 MiB │
│ Installed     │ BigQuery Command Line Tool                           │ bq                       │   < 1 MiB │
│ Installed     │ Cloud SDK Core Libraries                             │ core                     │   9.0 MiB │
│ Installed     │ Cloud Storage Command Line Tool                      │ gsutil                   │   3.5 MiB │
└───────────────┴──────────────────────────────────────────────────────┴──────────────────────────┴───────────┘
To install or remove components at your current SDK version [275.0.0], run:
  $ gcloud components install COMPONENT_ID
  $ gcloud components remove COMPONENT_ID

To update your SDK installation to the latest version [275.0.0], run:
  $ gcloud components update
```  

## Documentación:

* [Install Google Cloud SDK (ENG)](https://cloud.google.com/sdk/install/)

Revisado a 01/02/2020.

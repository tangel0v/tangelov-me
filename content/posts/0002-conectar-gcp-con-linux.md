---
title: "Conectando Google Cloud Platform (GCP) con Linux"
slug: conectar-gcp-con-linux
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

También podemos instalarlo a través de sus repositorios oficiales para [Ubuntu/Debian](https://cloud.google.com/sdk/docs/install#deb) o para distribuciones basadas en [RPM](https://cloud.google.com/sdk/docs/install#rpm).

### Configuración
Una vez ya hemos instalado la CLI, debemos iniciarla con
```bash
# Iniciamos el asistente de configuración de Google Cloud SDK
gcloud init --no-browser

Welcome! This command will take you through the configuration of gcloud.

Your current configuration has been set to: [default]

You can skip diagnostics next time by using the following flag:
  gcloud init --skip-diagnostics

Network diagnostic detects and fixes local network connection issues.
Checking network connection...done.                                                                   
Reachability Check passed.
Network diagnostic passed (1/1 checks passed).

You must log in to continue. Would you like to log in (Y/n)?  Y

You are authorizing gcloud CLI without access to a web browser. Please run the following command on a machine with a web browser and copy its output back here. Make sure the installed gcloud version is 372.0.0 or newer.
```
Nos aparecerá una URL que debemos copiar y pegar en un navegador:

![Configuracion de Google Cloud](https://storage.googleapis.com/tangelov-data/images/0002-00.png)

Y pegar el código resultante en la terminal.

Con esto ya estará configurado y si hacemos _gcloud config list_ podremos verla:

![Ejemplo de configuración](https://storage.googleapis.com/tangelov-data/images/0002-02.png)

Nuestra configuración se encuentra en una carpeta dentro de nuestro $HOME llamada _.config/.gcloud_:
```bash
.config
└── gcloud
    ├── access_tokens.db
    ├── active_config
    ├── application_default_credentials.json
    ├── config_sentinel
    ├── cache
        └── xxxxxxxxxxxx@gmail.com
            └── resource.cache
    ├── configurations
    │   └── config_default
    ├── credentials.db
    ├── gce
    ├── legacy_credentials
    │   └── xxxxxxxxxxxx@gmail.com
    │       └── adc.json
    └── logs
        └── 2022.12.04
            ├── 09.22.59.811541.log
            └── 09.24.17.024208.log
```

### Configuración extra
Si necesitamos alguno de los clientes extra que tiene Google Cloud como, por ejemplo, el usado por Big Table, debemos instalarlo. Para ello debemos usar el comando _gcloud components install $nombrecomponente_

También podemos ver todos los componentes disponibles con _gcloud components list_ :

```bash
Your current Cloud SDK version is: 411.0.0
The latest available version is: 411.0.0

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                 Components                                                 │
├───────────────┬──────────────────────────────────────────────────────┬──────────────────────────┬──────────┤
│     Status    │                         Name                         │            ID            │   Size   │
├───────────────┼──────────────────────────────────────────────────────┼──────────────────────────┼──────────┤
│ Not Installed │ App Engine Go Extensions                             │ app-engine-go            │  4.2 MiB │
│ Not Installed │ Appctl                                               │ appctl                   │ 21.0 MiB │
│ Not Installed │ Artifact Registry Go Module Package Helper           │ package-go-module        │  < 1 MiB │
│ Not Installed │ Cloud Bigtable Command Line Tool                     │ cbt                      │ 10.4 MiB │
│ Not Installed │ Cloud Bigtable Emulator                              │ bigtable                 │  6.7 MiB │
│ Not Installed │ Cloud Datastore Emulator                             │ cloud-datastore-emulator │ 35.1 MiB │
│ Not Installed │ Cloud Firestore Emulator                             │ cloud-firestore-emulator │ 40.2 MiB │
│ Not Installed │ Cloud Pub/Sub Emulator                               │ pubsub-emulator          │ 62.4 MiB │
│ Not Installed │ Cloud Run Proxy                                      │ cloud-run-proxy          │  9.0 MiB │
│ Not Installed │ Cloud SQL Proxy                                      │ cloud_sql_proxy          │  7.8 MiB │
│ Not Installed │ Cloud Spanner Emulator                               │ cloud-spanner-emulator   │ 28.7 MiB │
│ Not Installed │ Cloud Spanner Migration Tool                         │ harbourbridge            │ 18.1 MiB │
│ Not Installed │ Google Container Registry's Docker credential helper │ docker-credential-gcr    │  1.8 MiB │
│ Not Installed │ Kustomize                                            │ kustomize                │  4.3 MiB │
│ Not Installed │ Log Streaming                                        │ log-streaming            │ 13.9 MiB │
│ Not Installed │ Minikube                                             │ minikube                 │ 31.5 MiB │
│ Not Installed │ Nomos CLI                                            │ nomos                    │ 25.0 MiB │
│ Not Installed │ On-Demand Scanning API extraction helper             │ local-extract            │ 13.4 MiB │
│ Not Installed │ Skaffold                                             │ skaffold                 │ 20.1 MiB │
│ Not Installed │ Terraform Tools                                      │ terraform-tools          │ 53.3 MiB │
│ Not Installed │ anthos-auth                                          │ anthos-auth              │ 20.4 MiB │
│ Not Installed │ config-connector                                     │ config-connector         │ 56.7 MiB │
│ Not Installed │ gcloud app Java Extensions                           │ app-engine-java          │ 63.9 MiB │
│ Not Installed │ gcloud app Python Extensions                         │ app-engine-python        │  8.6 MiB │
│ Not Installed │ gcloud app Python Extensions (Extra Libraries)       │ app-engine-python-extras │ 26.4 MiB │
│ Not Installed │ gke-gcloud-auth-plugin                               │ gke-gcloud-auth-plugin   │  7.6 MiB │
│ Not Installed │ kubectl                                              │ kubectl                  │  < 1 MiB │
│ Not Installed │ kubectl-oidc                                         │ kubectl-oidc             │ 20.4 MiB │
│ Not Installed │ pkg                                                  │ pkg                      │          │
│ Installed     │ BigQuery Command Line Tool                           │ bq                       │  1.6 MiB │
│ Installed     │ Bundled Python 3.9                                   │ bundled-python3-unix     │ 62.2 MiB │
│ Installed     │ Cloud Datalab Command Line Tool                      │ datalab                  │  < 1 MiB │
│ Installed     │ Cloud Storage Command Line Tool                      │ gsutil                   │ 15.5 MiB │
│ Installed     │ Google Cloud CLI Core Libraries                      │ core                     │ 25.8 MiB │
│ Installed     │ Google Cloud CRC32C Hash Tool                        │ gcloud-crc32c            │  1.2 MiB │
│ Installed     │ gcloud Alpha Commands                                │ alpha                    │  < 1 MiB │
│ Installed     │ gcloud Beta Commands                                 │ beta                     │  < 1 MiB │
│ Installed     │ kpt                                                  │ kpt                      │ 12.3 MiB │
└───────────────┴──────────────────────────────────────────────────────┴──────────────────────────┴──────────┘
To install or remove components at your current SDK version [411.0.0], run:
  $ gcloud components install COMPONENT_ID
  $ gcloud components remove COMPONENT_ID

To update your SDK installation to the latest version [411.0.0], run:
  $ gcloud components update
```  

## Documentación:

* [Install Google Cloud SDK (ENG)](https://cloud.google.com/sdk/install/)

Revisado a 01/05/2023.

---
title: "Introducción a Jenkins: un clásico CI Open Source"
slug: ic-jenkins
authors:
  - tangelov
date: 2018-10-06T05:00:00+02:00
tags:  ["devops", "jenkins", "ci"]
categories: ["devops"]
draft: false
---

Tras haber probado alternativas (como [aquí](https://tangelov.me/posts/ic-gitlab.html) o [aquí](https://tangelov.me/posts/ic-github.html)), hoy vamos a hablar sobre el campeón de integración continua.

Jenkins es un programa escrito en Java de código abierto y que nos permite diseñar e implementar pautas de automatización en el proceso de creación y despliegue de software. Además de ser una potente herramienta de CI, es multiplataforma y gracias a un sistema de extensiones bastante potente podemos integrarlo con cualquier lenguaje y situación.  

Por ejemplo, nuestro Jenkins podría comprobar si el rendimiento de nuestra aplicación ha caído desde el último despliegue e impedir que se hiciera, comprobar si pasamos una serie de tests de calidad de forma automática o simplemente desplegar de forma automática en Pre-producción cada vez que alguien sube código a una rama en _git_ o en _subversion_.

<!--more-->

## Instalación y configuración
Ya existen tutoriales muy buenos sobre cómo instalar Jenkins en nuestro PC. En mi caso he decidido utilizar simplemente un contenedor Docker para ganar agilidad y levantarlo sólo cuando lo necesite.

> __Nota del autor__: En la primera versión de este post, se utilizaba Python 2 y se utilizaba una imagen de Docker oficial pero ahora vamos a generar una derivada para que el uso de Python 3 sea el predeterminado.

Primero creamos un Dockerfile con el siguiente contenido para crear una imagen personalizada de Jenkins con Python 3.

```Dockerfile
FROM jenkins/jenkins:lts

USER root
RUN apt-get update &&  \
  apt-get install python3-dev \
  python3 \
  python3-pip -y

USER jenkins
```

Ahora debemos construir la imagen con el comando ```docker build -t jenkins/jenkins:lts .``` o ```podman build -t jenkins/jenkins:lts .```, dependiendo del sistema que utilicemos para ejecutar contenedores.

Una vez ya hemos construido nuestra imagen, sólo necesitamos ejecutar este comando para tener un Jenkins totalmente funcional, independientemente del sistema operativo o de la distribución Linux que usemos:

```podman run -d -v jenkins_home:/var/jenkins_home -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts```


Vamos a explicarlo un poco:

* Obtenemos la versión LTS de Jenkins para que el mantenimiento sea más sencillo y duradero en el tiempo. Nos muestra los logs en tiempo real en la terminal desde la que lo lanzamos.

* Creamos un volumen llamado _jenkins_home_ que mapee _/var/jenkins_home/_ en el contenedor para que no perdamos los datos en el caso de actualizaciones o mantenimiento.

* Mapeamos a nuestro host dos puertos: 8080, el puerto desde el que nos conectaremos a Jenkins a través de nuestro navegador y 50000, el puerto con el que Jenkins se conectará a ejecutores externos mediante el protocolo [JNLP](https://es.wikipedia.org/wiki/Java_Network_Launching_Protocol).

Si necesitamos más información acerca de cómo configurar nuestros contenedores, la documentación de Jenkins al respecto es decente y puede consultarse [aquí](https://github.com/jenkinsci/docker/blob/master/README.md).

La primera vez que arrancamos Jenkins tendremos que crear un usuario administrador y nos pedirá permiso para instalar una serie de plugins. Le decimos que si y continuamos.

![interfaz-jenkins](https://storage.googleapis.com/tangelov-data/images/0016-00.png)

Para poder seguir este tutorial, debemos instalar el plugin para integrar Jenkins con Gitlab, que está disponible [aquí](https://github.com/jenkinsci/gitlab-plugin).


## Nuestro primer job de Jenkins
Como en otras pruebas de CI, vamos a utilizar como ejemplo el proceso de creación del contenido del blog, pero a diferencia de otras ocasiones, vamos a desplegarlo contra Google Cloud. En definitiva, nuestro job va a tener tres fases:

* Descarga del código fuente

* Creación del código HTML

* Publicación del código final en Google Cloud

En primer lugar vamos a crear una nueva credencial de Jenkins para que pueda acceder al contenido de Git a través de la API. Se hace en _Manage Jenkins/Manage Credentials/Stored Scopes to Jenkins/Global Credentials/Add Credentials_

![credencial-gitlab](https://storage.googleapis.com/tangelov-data/images/0016-02.png)

Después configuramos la conexión contra Gitlab en _Manage Jenkins/Configure System_:

![jenkins-gitlab](https://storage.googleapis.com/tangelov-data/images/0016-03.png) 


Ahora vamos a crear una nueva tarea y vamos hacer click en _New Item/Freestyle project_ y hacemos click en OK.

![creacion-job](https://storage.googleapis.com/tangelov-data/images/0016-01.png)

En la pestaña de _General_ seleccionamos la conexión de Gitlab que acabamos de generar

![nikola-job](https://storage.googleapis.com/tangelov-data/images/0016-04.png)

Y en la pestaña de _Source code management_, seleccionamos la rama que queremos utilizar y la forma de conectarnos. Si usamos SSH tendremos que añadir una nueva credencial con nuestra llave.

![gitlab-credentials](https://storage.googleapis.com/tangelov-data/images/0016-05.png)

Y finalmente en _Build_ añadimos el tipo de paso _Execute shell_ con el siguiente contenido:

![nikola-execution](https://storage.googleapis.com/tangelov-data/images/0016-06.png)

Con estos pasos, nuestro job se descargaría el código fuente y generaría el HTML final gracias a _nikola_, ahora vamos a añadir un paso más que lo desplegaría en Google Cloud. 

Para ello, primero debemos crear una cuenta de servicio en Google Cloud siguiendo [éste tutorial](https://cloud.google.com/iam/docs/creating-managing-service-accounts). Después lo añadimos como credencial en Jenkins y lo añadimos a nuestro job:

![gcloud-binding](https://storage.googleapis.com/tangelov-data/images/0016-07.png)

Ahora creamos un segundo paso en la construcción donde nos descargamos la CLI de Google y subimos el contenido generado por Nikola a nuestro app engine:

![nikola-deploy](https://storage.googleapis.com/tangelov-data/images/0016-08.png)

Nuestro job de Jenkins ya realiza todo lo que queremos :D


## Pipelines
El job anteriormente creado es visual, pero es secuencial y aunque sea fácil de configurar es poco flexible. ¿Y si queremos que nuestro job sea codificable? ¿Y si queremos paralelice partes del job? Todo es mucho más sencillo si utilizamos _pipelines_

Tanto un job como un _Pipeline_ son una serie de acciones que Jenkins interpreta y ejecuta, pero un pipeline nos permite codificarlo utilizando un lenguaje propio llamado DSL y Groovy. Esto nos permite crear ficheros de configuración en nuestros repositorios de código que Jenkins interpretará directamente al clonar el repositorio.

Jenkins soporta dos tipos de pipelines: declarativas y _scripted_:

* Las _scripted pipelines_ tienen una sintaxis completa y siguen un método de programación imperativo. Son más complejas pero permiten un control absoluto sobre el proceso de despliegue y test si el controlador de Jenkins las domina.

* Las pipelines declarativas tienen una sintaxis simple y nos permite ir definiendo paso a paso lo que queremos que haga nuestra variable. En caso de ser necesario, podemos intercalar partes de código _scripted_ en nuestros pipeliens declarativos.

Vamos a crear una nueva tarea de Jenkins de tipo pipeline y vamos a introducir este código

```groovy
pipeline {
    agent any
    environment {
        PATH = "/var/jenkins_home/.local/bin:/var/jenkins_home/workspace/test_pipeline_jenkins/tools/google-cloud-sdk/bin:$PATH"
    }
    
    stages {
        stage('Install prerrequisites') {
            steps {
                sh 'curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-426.0.0-linux-x86_64.tar.gz --output tools/gcloud.tar.gz'
                sh 'tar -xvf tools/gcloud.tar.gz -C tools/'
                
                sh 'pip3 install "nikola[extras]"==8.2.3 --user'
            }
        }
        
        stage('Getting the code and creating HTML code') {
            steps {
                git 'https://gitlab.com/tangelov/tangelov-me.git'
            
                sh '''
                nikola build
                '''
            }
        }
        
        stage('Deploying the code in GCP') {
            steps {
                sh '''
                gcloud config set core/project "$project-id"
                cd output && gcloud app deploy --quiet
                '''
            }
        }
    }
}
```

![gcloud-pipeline](https://storage.googleapis.com/tangelov-data/images/0016-09.png)

Este código replica lo que hemos realiado en el anterior job, pero a través del código. Se realizan tres pasos diferentes:

* En el primero descargamos e instalamos todas las herramientas necesarias para poder usar crear nuestro despliegue.

* En el segundo paso, descargamos el código de nuestro repositorio y generamos el código HTML

* Finalmente, desplegamos con la CLI de Google Cloud el contenido generado en un App Engine. 


## Documentación

* [Página oficial de Jenkins (ENG)](https://jenkins.io/)

* [Instalación y configuración de Jenkins en Ubuntu](https://medium.com/indigoit/instalar-y-configurar-jenkins-en-un-servidor-para-integraci%C3%B3n-continua-parte-1-78b1a8a749c4)

* [Integración de Jenkins y Gitlab](https://docs.gitlab.com/ee/integration/jenkins.html) 

* [Configuración de tokens entre Jenkins y Gitlab](https://github.com/jenkinsci/gitlab-plugin/wiki/Setup-Example)

* [Pipelines en Jenkins (ENG)](https://jenkins.io/doc/book/pipeline/)

* [La integración continua pasa por pipelines](https://sdos.es/integracion-continua-pasa-por-pipelines/)


Revisado a 01/05/2023

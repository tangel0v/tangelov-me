---
title: "Skaffold: construcción y despliegue multipropósito"
slug: cloud-deploy-i
authors:
  - tangelov
date: 2025-01-13T10:00:00+02:00
tags:  ["terraform", "gcp", "cicd"]
categories: ["devops"]
draft: false
---

## Introducción
Hace 30 años, la informática era más pausada de lo que lo es en la actualidad. Si queríamos introducir una nueva herramienta, al igual que ahora, se realizaba una prueba de concepto a pequeña escala para probar sus funcionalidades antes de pasar a su uso generalizado.

Eran pruebas lentas y muy intensivas en recursos: cada herramienta requería de su propio sistema de instalación y configuración. La aparición de Docker en 2013, transformó este tipo de escenarios pues al crear paquetes portables, estandarizó el proceso y redujo el esfuerzo necesario para introducir nuevas herramientas o servicios.

A día de hoy, Docker es el estándar _de facto_ a la hora de distribuir aplicaciones, pero para desplegarlas existen múltiples herramientas (Jenkins, ArgoCD, etc), que convierten el proceso en algo muy heterogéneo. Tratando de simplificar aún más el proceso es cómo descubrí __Skaffold__.

En este post vamos a utilizar dicha herramienta para construir y desplegar una pequeña aplicación (este blog) en varios entornos (en Docker y directamente en la nube en un servicio de Cloud Run). Espero que os guste.

<!--more-->

## Skaffold
Para crear una imagen y ejecutar nuestra aplicación en contenedores, tradicionalmente necesitaríamos un Dockerfil (un fichero que contiene las instrucciones para descargar las dependencias de nuestra aplicación), añadir nuestro código y un sistema para ejecutarlo. Dependiendo de nuestras necesidades, este proceso puede realizarse en local o en remoto, de forma automática o manual y con multitud de opciones para realizar el proceso.

Nuestra imagen tiene que almacenarse en un repositorio para que pueda ser distribuida entre nuestros servidores de una forma óptima, añadiendo aún más herramientas al proceso.

Skaffold es una CLI desarrollada por Google, que permite a los desarrolladores estandarizar el proceso de construcción y despliegue de contenedores añadiendo un simple fichero de configuración.

Skaffold nos permite generar perfiles donde podemos construir, probar y desplegar utilizando una gran cantidad de métodos. Para ver todas sus funcionalidades, podemos acceder [aquí](https://skaffold.dev/docs/pipeline-stages/).

Para comenzar a utilizarlo, sólo tenemos que descargarnos la CLI y darle permisos de ejecución:

```bash
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64 && \
sudo install skaffold /usr/local/bin/
```

A nivel interno, Skaffold define un pipeline de CICD al completo como código y que tiene los siguientes pasos o _stages_:

0. __Init__: Este paso previo detecta configuraciones ya conocidas y nos guía para generar el fichero de configuración utilizado por Skaffold.
1. __Build__: Este paso es el encargado de generar la imagen de nuestro contenedor utilizando distintos _builders_. Aquí podremos definir características como la política de etiquetado de las imágenes
2. __Test__: Este paso permite realizar ciertas comprobaciones entre la fase de _Build_ y la de _Deploy_.
3. __Render__: Este paso se encarga de crear la definición de los servicios donde vamos a desplegar nuestra imagen. Se utiliza fundamentalmente cuando nuestros servicios van a desplegarse en Kubernetes.
4. __Deploy__: Gracias a la imagen creada en el paso 1 y a los servicios definidos en el paso 3, el _step Deploy_ se encarga de desplegar nuestra aplicación en un servicio compatible (Kubernetes, Cloud Run y Docker).
5. __Verify__: Permite utilizar otros contenedores para asegurarnos que nuestro despliegue ha salido bien.

En este post, vamos a crear una _pipeline_ básica que simplemente construya un contenedor y lo despliegue en un destino. La imagen que he elegido es la que se encuentra en el [repositorio de este mismo blog](https://gitlab.com/tangelov/go-tangelov-me/-/blob/main/Dockerfile).

### Build
Skaffold busca abstraernos del sistema de construcción de contenedores y se conecta a una gran cantidad de ellos de forma nativa. A día de hoy, puede utilizar Dockerfiles, Jib, Maven y Gradle (para aplicaciones desarrolladas en Java), Buildpacks, Bazel, Ko o scripts personalizados. Para más información al respecto, me remito a la [documentación oficial](https://skaffold.dev/docs/builders/).

Para comenzar a utilizarlo, creamos un fichero con el nombre _skaffold.yaml_ en nuestro repositorio, con el siguiente contenido, o ejecutar ```skaffold init```:

```yaml
apiVersion: skaffold/v4beta11
kind: Config
metadata:
  name: tangelov-with-skafold
build:
  tagPolicy:
    sha256: {}
  artifacts:
   - image: tangelov
     docker:
       dockerfile: ./Dockerfile
  local:
    useDockerCLI: false
    useBuildkit: false
```

Este fichero le indica a Skaffold que debe de crear una imagen en local utilizando Docker o algún servicio compatible con el mismo. Debido a que yo estoy utilizando Podman (podéis ver más información [aquí](https://tangelov.me/posts/containers-without-docker.html)) necesitamos realizar un par de pasos extra (crear un repositorio donde poder almacenar la imagen creada y definir una variable de entorno).

```bash
# Nos descargamos la imagen necesaria para guardar imagenes de DockerHub y lo ejecutamos para que escuche en el puerto 5000
podman container run -dt -p 5000:5000 --name registry --volume registry:/var/lib/registry:Z --restart=always docker.io/library/registry:2

# Ahora ya podemos crear y almacenar contenedores en local

# También necesitamos cambiar $ID por el que tenga nuestro usuario. Suele ser el 1000, pero dependiendo de nuestro usuario puede variar
# No es necesario si utilizar Docker Desktop o Docker Engine
export DOCKER_HOST='unix:///run/user/$ID/podman/podman.sock'
```

Para que la imagen se almacene de forma correcta en un repositorio, tenemos que cambiar su nombre de la siguiente manera:

```bash
apiVersion: skaffold/v4beta11
kind: Config
metadata:
  name: tangelov-with-skafold
build:
  tagPolicy:
    gitCommit:
      variant: AbbrevCommitSha
      ignoreChanges: true
  artifacts:
   - image: localhost:5000/tangelov
     docker:
       dockerfile: ./Dockerfile
  local:
    useDockerCLI: false
    useBuildkit: false
```

Los cambios modifican el comportamiento de Skaffold:
- Se define un sistema para etiquetar las imágenes con el commit del último cambio del repositorio de código donde esté la aplicación.
- El nombre de la imagen será _tangelov_ y utilizará un _Dockerfile_ ubicado en la misma carpeta donde se encuentre _skaffold.yaml_. Se almacenará en un repositorio que escucha en localhost:5000.

Ahora ejecutamos ```skaffold build``` sin más problemas:

```bash
skaffold build

```bash
Generating tags...
 - localhost:5000/tangelov -> localhost:5000/tangelov:c7c4529
Checking cache...
 - localhost:5000/tangelov: Not found. Building
Starting build...
Building [localhost:5000/tangelov]...
Sending build context to Docker daemon  4.499MB
STEP 1/2: FROM nginx:stable-alpine
STEP 2/2: COPY public /usr/share/nginx/html
--> Using cache c5ad9a38a33355fe0298ed14d887a484241425584233c6eff3370ec656c60e01
COMMIT localhost:5000/tangelov:c7c4529
--> c5ad9a38a333
Successfully tagged localhost:5000/tangelov:c7c4529
Successfully tagged docker.io/library/tangelov:latest
c5ad9a38a33355fe0298ed14d887a484241425584233c6eff3370ec656c60e01
Successfully built c5ad9a38a333
Successfully tagged localhost:5000/tangelov:c7c4529
The push refers to repository [localhost:5000/tangelov:c7c4529]
c7c4529: digest: sha256:0ed3899f94d2e911e30e346a525a62804050d938436e0095ff971af8129b948b size: 1682
```

Si accedemos a nuestro repositorio de imágenes, podemos ver la imagen recién creada allí:

```bash
docker images
Emulate Docker CLI using podman. Create /etc/containers/nodocker to quiet msg.
REPOSITORY                  TAG            IMAGE ID      CREATED         SIZE
localhost:5000/tangelov     latest         3d888219c18c  58 minutes ago  54.7 MB
docker.io/library/nginx     stable-alpine  60847f99ea69  4 months ago    50.2 MB
docker.io/library/registry  2              c18a86d35e98  15 months ago   26 MB
```

### Deploy
La construcción es sólo una parte del proceso total de CICD. En este apartado vamos a añadir la parte de despliegue.

El concepto es el mismo: añadir una abstracción que se integra de forma nativa con las herramientas de despliegue más habituales para sistemas basados en contenedores (como Docker, Kubectl o Helm). Si nuestra herramienta no está soportada, podemos definir acciones personalizadas e integrar Skaffold con casi cualquier cosa.

Nosotros vamos a coger nuestra imagen recién creada y vamos a desplegarla en dos destinos distintos: en un Docker y en un clúster de Kubernetes en local. De esta forma podemos ver el funcionamiento de Skaffold en un entorno más realista y las funcionalidades que posee.

Añadimos la fase de _deploy_, dejando la configuración de la siguiente manera:

```yaml
apiVersion: skaffold/v4beta11
kind: Config
metadata:
  name: tangelov-with-skafold
build:
  tagPolicy:
    gitCommit:
      variant: AbbrevCommitSha
      ignoreChanges: true
  artifacts:
   - image: tangelov
     docker:
       dockerfile: ./Dockerfile
  local:
    useDockerCLI: false
    useBuildkit: false
    push: false
deploy:
  docker:
    images: [tangelov]
```

Las modificaciones le indican a Skaffold que:
- No debe _pushear_ la imagen a ningún repositorio.
- El nombre es simplemente _tangelov_.
- Dicha imagen local tiene que desplegarla en el cluster local de Docker.

Si ejecutamos `skaffold run --tail` podemos ver el proceso completo (creación y despliegue):

```bash
skaffold run --tail
Generating tags...
 - tangelov -> tangelov:c7c4529
Checking cache...
 - tangelov: Found Locally
Starting test...
Tags used in deployment:
 - tangelov -> tangelov:cc522fb0612781af984f3104a238202505ce6faf5af34ffbd97633ccd1183d8a
Starting deploy...
Press Ctrl+C to exit
[tangelov] /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
[tangelov] /docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
[tangelov] /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
[tangelov] 10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
[tangelov] 10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
[tangelov] /docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
[tangelov] /docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
[tangelov] /docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
[tangelov] /docker-entrypoint.sh: Configuration complete; ready for start up
[tangelov] 2025/01/06 12:46:28 [notice] 1#1: using the "epoll" event method
[tangelov] 2025/01/06 12:46:28 [notice] 1#1: nginx/1.26.2
[tangelov] 2025/01/06 12:46:28 [notice] 1#1: built by gcc 13.2.1 20240309 (Alpine 13.2.1_git20240309) 
[tangelov] 2025/01/06 12:46:28 [notice] 1#1: OS: Linux 5.10.207
[tangelov] 2025/01/06 12:46:28 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
[tangelov] 2025/01/06 12:46:28 [notice] 1#1: start worker processes
[tangelov] 2025/01/06 12:46:28 [notice] 1#1: start worker process 30
[tangelov] 2025/01/06 12:46:28 [notice] 1#1: start worker process 31
```

Como podemos ver, Skaffold primero ha comprobado que la imagen no existiese previamente y después lo ha desplegado de forma exitosa :)

Una vez hemos verificado el despliegue sobre Docker, vamos a continuar con Kubernetes. Para ello, primero vamos a crear un cluster en local y la forma más fácil de hacerlo es utilizando _Minikube_: simplemente lo descargamos, ejecutamos `minikube start` y ya podemos empezar a interactuar con él.

Al desplegar sobre Kubernetes, necesitamos crear la definición de los servicios que va a desplegar, un _manifest_ que permita a nuestra aplicación gestionarse y ser expuesta fuera del clúster. Para ello creamos un fichero llamado _k8s.yaml_ y pegamos el siguiente contenido:

```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tangelov-deployment
  labels:
    app: tangelov
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tangelov
  template:
    metadata:
      labels:
        app: tangelov
    spec:
      containers:
      - name: tangelov
        image: tangelov
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: tangelov-service
spec:
  selector:
    app: tangelov
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: NodePort
```

Este fichero define un _Deployment_ que controla nuestro contenedor, creando una réplica del mismo y un _Service_ que nos permite acceder a dicho servicio a través de un _NodePort_ en el nodo donde se despliegue.

Con esta nueva configuración, podemos hacer que Skaffold despliegue nuestra aplicación en Kubernetes utilizando las plantillas que acabamos de definir junto a Docker:

```yaml
apiVersion: skaffold/v4beta11
kind: Config
metadata:
  name: tangelov-with-skafold
build:
  tagPolicy:
    gitCommit:
      variant: AbbrevCommitSha
      ignoreChanges: true
  artifacts:
   - image: tangelov
     docker:
       dockerfile: ./Dockerfile
  local:
    useDockerCLI: false
    useBuildkit: false
    push: false
deploy:
  docker:
    images: [tangelov]
manifests:
  rawYaml:
  - k8s*
```
Esto se consigue añadiendo un apartado llamado _manifests_, que utilizará un fichero RAW cuyo nombre comienza por k8s.

Si ejecutamos otra vez `skaffold run` veremos un poco de información extra:

```bash
skaffold run                                                                        
Generating tags...
 - tangelov -> tangelov:c7c4529
Checking cache...
 - tangelov: Found Locally
Starting test...
Tags used in deployment:
 - tangelov -> tangelov:cc522fb0612781af984f3104a238202505ce6faf5af34ffbd97633ccd1183d8a
Starting deploy...
 - deployment.apps/tangelov-deployment configured
 - service/tangelov-service created
Waiting for deployments to stabilize...
 - deployment/tangelov-deployment is ready.
Deployments stabilized in 2.129 seconds
```

Y si tratamos de acceder a la aplicación a través del NodePort... funciona como esperaríamos:

![tangelov-in-k8s](https://storage.googleapis.com/tangelov-data/images/0058-00.png)


## Skaffold... en la nube
Skaffold no sólo permite diseñar procesos en local, sino también replicarlos en la nube de forma sencilla. Al ser desarrollado por Google, tiene integración nativa con algunos servicios de GCP, pero para otros proveedores sería necesario crear acciones personalizadas.

Para este nuevo apartado, vamos a construir nuestra imagen de forma remota en Cloud Build y a desplegarla en Cloud Run.

### Construcción con Cloud Build

Antes de nada, necesitamos realizar tres pasos previos:
1. Habilitamos la API de _Artifact Registry_ en GCP y crear un repositorio donde nuestra imagen ser almacenada (Para que pueda desplegarse en Cloud Run)
2. Habilitamos la API de _Cloud Build_ en GCP para que dicho servicio funcione.
3. Tenemos que tener permisos para usar ambos servicios y autenticarnos ante la Google Cloud usando su CLI y el comando ```gcloud auth login```

Una vez hemos cumplido con los pasos anteriores, tan sólo modificamos nuestro fichero _skaffold.yaml_ para que tenga el siguiente contenido:

```yaml
apiVersion: skaffold/v4beta11
kind: Config
metadata:
  name: tangelov-with-skafold
build:
  tagPolicy:
    gitCommit:
      variant: AbbrevCommitSha
      ignoreChanges: true
  googleCloudBuild:
    projectId: "CENSORED"
    region: "europe-west1"
    machineType: "E2_MEDIUM"
  artifacts:
   - image: europe-west1-docker.pkg.dev/CENSORED/skaffold/tangelov
     docker:
       dockerfile: Dockerfile
```

Gracias a estos cambios, la construcción ha pasado a realizarse en remoto dentro de Cloud Build, que debemos configurar con algunos parámetros:
* El identificador del proyecto dentro de Google Cloud donde se va a crear la imagen (_CENSORED_, debemos cambiar dicha palabra por el ID de nuestro proyecto)
* La región donde se va a ejecutar todo el proceso (_region_). Si no indicamos región alguna, el sistema seleccionará _global_ automáticamente.
* El tamaño de la instancia que vamos a utilizar para construir la imagen. En este caso utilizamos _E2\_MEDIUM_ porque la imagen se construye muy rápidamente.
* El nombre de la imagen es distinto para indicarle al servicio donde tiene que almacenarla una vez haya terminado de construirla.

Si ahora ejecutamos ```skaffold build``` veremos lo siguiente:

```bash
skaffold build
Generating tags...
 - europe-west1-docker.pkg.dev/$CENSORED/skaffold/tangelov -> europe-west1-docker.pkg.dev/$CENSORED/skaffold/tangelov:677b093
Checking cache...
 - europe-west1-docker.pkg.dev/$CENSORED/skaffold/tangelov: Not found. Building
Starting build...
Building [europe-west1-docker.pkg.dev/$CENSORED/skaffold/tangelov]...
Pushing code to gs://${CENSORED}_cloudbuild/source/$CENSORED-MY-BUILD-ID.tar.gz
Logs are available at 
https://storage.cloud.google.com/${CENSORED}_cloudbuild/log-MY-BUILD-ID.txt
starting build "MY-BUILD-ID"

FETCHSOURCE
Fetching storage object: gs://${CENSORED}_cloudbuild/source/CENSORED-MY-BUILD-ID.tar.gz#1736679784678146
Copying gs://${CENSORED}_cloudbuild/source/$CENSORED-MY-BUILD-ID.tar.gz#1736679784678146...
- [1 files][828.8 KiB/828.8 KiB]                                                
Operation completed over 1 objects/828.8 KiB.                                    
BUILD
Already have image (with digest): gcr.io/cloud-builders/docker
Sending build context to Docker daemon  4.532MB
Step 1/2 : FROM nginx:stable-alpine
stable-alpine: Pulling from library/nginx
66a3d608f3fa: Pulling fs layer
425c7b6b0584: Pulling fs layer
bc3151b8c483: Pulling fs layer
32c1c5ad4705: Pulling fs layer
acc3b7ea73b8: Pulling fs layer
b527c1980d34: Pulling fs layer
ea697fe9913f: Pulling fs layer
2504415565d4: Pulling fs layer
32c1c5ad4705: Waiting
acc3b7ea73b8: Waiting
b527c1980d34: Waiting
ea697fe9913f: Waiting
2504415565d4: Waiting
bc3151b8c483: Download complete
425c7b6b0584: Verifying Checksum
425c7b6b0584: Download complete
66a3d608f3fa: Verifying Checksum
66a3d608f3fa: Download complete
acc3b7ea73b8: Verifying Checksum
acc3b7ea73b8: Download complete
32c1c5ad4705: Download complete
ea697fe9913f: Verifying Checksum
ea697fe9913f: Download complete
b527c1980d34: Download complete
66a3d608f3fa: Pull complete
2504415565d4: Verifying Checksum
2504415565d4: Download complete
425c7b6b0584: Pull complete
bc3151b8c483: Pull complete
32c1c5ad4705: Pull complete
acc3b7ea73b8: Pull complete
b527c1980d34: Pull complete
ea697fe9913f: Pull complete
2504415565d4: Pull complete
Digest: sha256:b9e1705b69f778dca93cbbbe97d2c2562fb26cac1079cdea4e40d1dad98f14fe
Status: Downloaded newer image for nginx:stable-alpine
 ---> 4ebaceb1bd2e
Step 2/2 : COPY public /usr/share/nginx/html
 ---> 89097ff21c7a
Successfully built 89097ff21c7a
Successfully tagged europe-west1-docker.pkg.dev/$CENSORED/skaffold/tangelov:677b093
PUSH
Pushing europe-west1-docker.pkg.dev/$CENSORED/skaffold/tangelov:677b093
The push refers to repository [europe-west1-docker.pkg.dev/$CENSORED/skaffold/tangelov]
589ff11766eb: Preparing
9913e2a3170f: Preparing
f80a8fac336f: Preparing
ee128c8f01aa: Preparing
abd7f33ec37d: Preparing
f8faf11c609e: Preparing
3012f2d5c309: Preparing
ffebbad4cff8: Preparing
ce5a8cde9eee: Preparing
f8faf11c609e: Waiting
3012f2d5c309: Waiting
ffebbad4cff8: Waiting
ce5a8cde9eee: Waiting
abd7f33ec37d: Pushed
ee128c8f01aa: Pushed
f80a8fac336f: Pushed
589ff11766eb: Pushed
f8faf11c609e: Pushed
3012f2d5c309: Pushed
ce5a8cde9eee: Pushed
ffebbad4cff8: Pushed
9913e2a3170f: Pushed
677b093: digest: sha256:f31d279af94aeffa0954da7acbcc4d3b9bdd0947a427ffa65fadebb289524299 size: 2199
DONE
Build [europe-west1-docker.pkg.dev/$CENSORED/skaffold/tangelov] succeeded
```

El servicio realiza los siguientes pasos:
1. Genera los tags de las imágenes que vamos a crear
2. Sube el código local en un paquete a Cloud Storage.
3. Cloud Build descarga el constructor para Docker (por defecto es _gcr.io/cloud-builders/docker_)
4. Utilizando dicho constructor, sigue las instrucciones indicadas en el Dockerfile.
5. Por último, sube la imagen al repositorio que habíamos creado previamente.

> Si queremos que Cloud Build no suba a la nube partes de nuestro código, tenemos que crear un fichero .gcloudignore. Más información [aquí](https://gist.github.com/akiray03/6e37bfcdea1399beecf3cabde04f6cb0).

Si vamos a la consola, podemos nuestra imagen imagen en su repositorio:

![tangelov-cloud-build](https://storage.googleapis.com/tangelov-data/images/0058-01.png)

Y por supuesto, podemos usarla en un contenedor y ver que es similar a la que hemos creado antes en local:

```bash
podman container run -dt -p 80:8080 europe-west1-docker.pkg.dev/$CENSORED/skaffold/tangelov:677b093
```

![tangelov-cloud-build-ii](https://storage.googleapis.com/tangelov-data/images/0058-02.png)

### Despliegue en Cloud Run

Al igual que en el paso anterior, antes de poder desplegar sobre Cloud Run, necesitamos cumplir unos prerrequisitos:
1. Habilitamos la API de _Cloud run_ en GCP para que dicho servicio funcione.
2. Generamos un token de _application default credentials_ con el siguiente comando `gcloud auth application-default login`
3. Instalamos una [serie de paquetes](https://skaffold.dev/docs/deployers/cloudrun/#environment-setup) (Log Streaming, Cloud Run Proxy) en la CLI para tener acceso a todas las funcionalidades.

> Si hemos instalado la CLI de Google Cloud con nuestro gestor de paquetes tendremos que ejecutar `sudo apt-get install google-cloud-cli-log-streaming google-cloud-cli-cloud-run-proxy` (en Ubuntu/Debian).

Cumplidos los prerrequisitos, pasamos a configurar Cloud Run. Este servicio es una implementación propia de [KNative dentro de Google Cloud](https://cloud.google.com/blog/products/serverless/knative-based-cloud-run-services-are-ga) por lo que utiliza los mismos ficheros de configuración. Vamos a crear un fichero llamado _cloudrun.yaml_ con el siguiente contenido:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: tangelov-cloud-run 
spec:
  template:
    spec:
      containers:
      - image: europe-west1-docker.pkg.dev/CENSORED/skaffold/tangelov
        ports:
        - containerPort: 80
```

Este fichero crea un servicio llamado _tangelov-cloud-run_ basada en la imagen que hemos construido en el paso de _build_ y cuyo contenedor está escuchando en el puerto 80.

Solo nos faltaría configurar el despliegue dentro del fichero de configuración de Skaffold:

```yaml
apiVersion: skaffold/v4beta11
kind: Config
metadata:
  name: tangelov-with-skafold
build:
  tagPolicy:
    gitCommit:
      variant: AbbrevCommitSha
      ignoreChanges: true
  googleCloudBuild:
    projectId: "CENSORED"
    region: "europe-west1"
    machineType: "E2_MEDIUM"
  artifacts:
   - image: europe-west1-docker.pkg.dev/CENSORED/skaffold/tangelov
     docker:
       dockerfile: Dockerfile
manifests:
  rawYaml:
    - cloudrun.yaml 
deploy:
  cloudrun:
    projectid: "CENSORED"
    region: "europe-west1"
```

Como se puede observar, le hemos indicado en la parte de despliegue en que proyecto y región debe realizarse, así cómo el fichero YAML que contiene la definición del servicio de Cloud Run.

Al hacer `skaffold run` otra vez veremos que se lanza el proceso al completo y que en este caso se realiza también la parte del despliegue:

```bash
skaffold run

Generating tags...
 - europe-west1-docker.pkg.dev/CENSORED/skaffold/tangelov -> europe-west1-docker.pkg.dev/CENSORED/skaffold/tangelov:677b093
Checking cache...
 - europe-west1-docker.pkg.dev/CENSORED/skaffold/tangelov: Found Remotely
Starting test...
Tags used in deployment:
 - europe-west1-docker.pkg.dev/CENSORED/skaffold/tangelov -> europe-west1-docker.pkg.dev/CENSORED/skaffold/tangelov:677b093@sha256:f31d279af94aeffa0954da7acbcc4d3b9bdd0947a427ffa65fadebb289524299
Starting deploy...
Deploying Cloud Run service:
         tangelov-cloud-run
tangelov-cloud-run: Service starting: Revision waiting for Route initialization to complete.
[...]
tangelov-cloud-run: Service starting: Container image import in progress. Imported 7 of 16 layers.
Cloud Run Service tangelov-cloud-run finished: Service started. 0/1 deployment(s) still pending
```

Para comprobar que todo vaya bien, sólo tenemos que deshabilitar la autenticación de nuestro servicio y ya podemos disfrutar de él:

![tangelov-cloud-run](https://storage.googleapis.com/tangelov-data/images/0058-03.png)

![tangelov-cloud-run-ii](https://storage.googleapis.com/tangelov-data/images/0058-04.png)

¡Eso es todo! 

Un abrazo y nos vemos en el siguiente post.

## Documentación

* [Página oficial de Skaffold (ENG)](https://skaffold.dev/)

* [Cross-platform and multi-platform build support (ENG)](https://skaffold.dev/docs/builders/cross-platform/)

* [Builders en Skaffold (ENG)](https://skaffold.dev/docs/builders/)

* [Referencia de la estructura de skaffold.yaml (ENG)](https://skaffold.dev/docs/references/yaml/)

* [Skaffold - using Podman and Kind (ENG)](https://github.com/bkuzmic/skaffold-podman-kind)

* [Tutorial: Host a local Podman image registry (ENG)](https://thenewstack.io/tutorial-host-a-local-podman-image-registry/)

* [Deployers en Skaffold (ENG)](https://skaffold.dev/docs/deployers/)

* [Pushing and Pulling Docker images to/from Artifact Registry (ENG)](https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling)

* [Build with Skaffold in Cloud Build (ENG)](https://skaffold.dev/docs/builders/build-environments/cloud-build/)

* [Deploy with Skaffold in Cloud Run (ENG)](https://skaffold.dev/docs/deployers/cloudrun/)

* [Configure services in Cloud Run (ENG)](https://cloud.google.com/run/docs/configuring/services/containers#yaml_1)

Revisado a 13-01-2025

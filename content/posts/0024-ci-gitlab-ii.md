---
title: "Integración continua con Gitlab (II): refactorizando Tangelov.me"
slug: ic-gitlab-ii
authors:
  - tangelov
date: 2019-06-15T18:00:00+02:00
tags:  ["devops", "gitlab", "ci"]
categories: ["devops"]
draft: false
---

Hace más de un año que decidí empezar a escribir este blog. Aunque tuve dudas sobre qué stack o tecnologías utilizar o investigar, siempre supe que mi código iba a ir a _Gitlab_.

A lo largo de este año han ocurrido muchas cosas respecto a sistemas de gestión de código: Microsoft compró Github y ahora ofrecen repositorios privados de código gratis, el SaaS de [Gitlab](gitlab.com) cambió de proveedor de nube pública (de Microsoft Azure a Google Cloud Platform) y de paradigma conceptual (de monolitos a microservicios y contenedores) y Gitea, un hermano pequeño de Github escrito en Go ha empezado a ser una alternativa potente a tener en cuenta.

<!--more-->

Los sistemas de gestión de código han ido evolucionando poco a poco en una plataforma donde podemos almacenar, compilar, integrar, realizar análisis de seguridad y gestionar los procesos del equipo de desarrollo de la manera más automática posible.

En este post vamos a avanzar un poco más con Gitlab CI y a evolucionarlo a un proceso de CI/CD casi completo.


## Un pequeño recordatorio
Ya hice una pequeña demo hace meses con el sistema de _Pipelines_ de Gitlab: son potentes, autogestionados y fáciles de utilizar. En [aquel post](https://tangelov.me/posts/ic-gitlab.html) cogí el código de este blog, generé el HTML estático y lo integré en un contenedor, que finalmente subí a Dockerhub. Era una prueba de concepto para probar el servicio, aunque se alejaba un poco de las necesidades reales del blog.

También escribí en el pasado sobre cómo opero el blog y sobre [cómo está montada esta web](https://tangelov.me/posts/como-montada-web-i.html). El proceso de subida de código y despliegue sigue siendo manual y para publicar un post, hago paso a paso las siguientes operaciones:

* Primero subo las imágenes del blog a una carpeta dentro de un Cloud Storage que almacena los estáticos.

* Después hago _git push_ y subo el código a una rama nueva con el formato _post/codigo-de-post_ a Gitlab.

* Abro un _merge request_, reviso el código y si todo va bien, lo apruebo y lo mergeo contra la rama _master_.

* Finalmente, vuelvo a la terminal y ejecuto el comando _nikola build && nikola deploy gcloud_ que despliega el HTML generado a Google App Engine y lo hace visible a todo el mundo.

Es un proceso que no me ha dado problemas y es rápido, pero también es repetitivo y por ello fácilmente automatizable.


## Automatizando paso a paso


### Subiendo imágenes con hooks de git
Analizando los pasos del despliegue, vemos rápidamente que son dos partes independientes: una relacionada con la gestión del código en git y otra con la gestión de las imágenes fuera de él. Aunque _técnicamente_ sean independientes, _realmente_ no deberían serlo y las fotos deberían subirse a la nube automáticamente.

Para conseguir dicha funcionalidad, he decidido implementar _hooks_ en git. Los _git hooks_ son una funcionalidad embebida de git que hace que se ejecuten una serie de scripts antes o después de determinados eventos como pueden ser un _commit_, un _push_ o un _receive_.

Lo primero es conseguir un poco de orden. Actualmente guardaba las fotos directamente en la carpeta _Imágenes_ pero he creado una carpeta dentro del proyecto llamada _gcp-images_ y a añadirla al _gitignore_. Así agrupo todo el contenido y genero un único punto de subida para todas las imágenes del blog, manteniéndolas fuera de git. El resultado sería similar a éste:

![images-example](https://storage.googleapis.com/tangelov-data/images/0024-00.png)

Ahora vamos a configurar un hook. Git proporciona una serie de plantillas dentro de la ruta _.git/hooks_:

```bash
tangelov@tangelovers ls .git/hooks/
applypatch-msg.sample      pre-applypatch.sample      pre-rebase.sample
commit-msg.sample          pre-commit.sample          pre-receive.sample
fsmonitor-watchman.sample  prepare-commit-msg.sample  update.sample
post-update.sample         pre-push.sample
```

Los hooks son tremendamente versátiles y podemos usarlos para comprobar la sintáxis de nuestro código, enviar una notificación y hacer una acción totalmente personalizada. En mi caso, debido a que yo nunca subo el código a Gitlab hasta que esté bastante maduro (muy poco antes del despliegue a producción), voy a configurar el hook _pre-push_ para que cumpla las siguientes premisas:

* La rama local debe cumplir la política de nombres siguiente:
    * _feature/description_ se utiliza cuando se añaden mejoras al blog.
    * _fix/description_ se utiliza cuando se corrigen errores.
    * _post/description_ es el nombre de rama que utilizo cuando voy a escribir un nuevo artículo.
    * _page/description_ es el nombre que uso cuando genero una nueva página.

* Si las comprobaciones anteriores son correctas, las imágenes se suben a Cloud Storage.

* Si no hay errores en las comprobaciones anteriores, se subirán las imágenes a Cloud Storage. 
Cualquier hook que implementemos, se queda por defecto fuera del repositorio, así que lo he añadido al mismo como una plantilla en la carpeta _hooks_:

```bash
#!/bin/bash

GIT_BRANCH=`git rev-parse --abbrev-ref HEAD | tr '[:upper:]' '[:lower:]'`
SOURCE_PATH=""
DEST_PATH=''

if [[ "$GIT_BRANCH" == post/* ]] || [[ "$GIT_BRANCH" == page/*  ]]; then
        :

elif [[ "$GIT_BRANCH" == feature/* ]] || [[ "$GIT_BRANCH" == fix/* ]]; then
        :

else
        echo "Bad branch naming convention or WIP branch. Fix it and retry later."
        exit 1
fi

# Cloning images in Cloud Storage
if [[ "$SOURCE_PATH" == "" ]]; then
        echo "Source path not complete"
        exit 1
elif [[ "$DEST_PATH" == '' ]]; then
        echo "Destination PATH not complete"
        exit 1
else
        gsutil -m rsync $SOURCE_PATH $DEST_PATH
        exit 0
fi
```

El script es básico: comprueba que la rama local (siempre uso el mismo nombre en local y en remoto) cumple los requisitos y en caso afirmativo, sube las imágenes a la nube.

Si ahora intentáramos hacer _push_ desde una rama con un nombre incorrecto, recibiríamos este error:

```bash
tangelov@tangelovers git push origin post/gitlab-ci-ii

Bad branch naming convention or WIP branch. Fix it and retry later.
error: falló el push de algunas referencias a 'git@gitlab.com:tangelov/tangelov-me.git'
```

### Desplegando contra Google Cloud
Tras integrar la subida de imágenes en nuestro flujo de trabajo, vamos a mejorar el pipeline definido en _.gitlab-ci.yml_ para conseguir lo siguiente:

* Al pushear a Gitlab en una nueva rama, generaremos una nueva versión en App Engine para hacer pruebas. El nombre será configurable a través de variables de Gitlab.

* Se harán una serie de tests automáticos en esa nueva versión para verificar que todo funciona y que se ha añadido nuevo contenido al blog.

* El paso final de desplegar a Producción se realizará automáticamente cuando todos los pasos anteriores se hayan realizado correctamente, tras hacer un _merge request_ a master.


#### Preparación del entorno
Lo primero que tenemos que hacer es crear una cuenta de servicio dentro de GCP que podamos usar desde Gitlab. Utilizando los permisos más restrictivos posibles, tendrá las siguientes características:

* Permisos de _App Engine Deployer_ (para desplegar y eliminar versiones de GAE), _App Engine Service Admin_ (para cambiar el tráfico a cada versión) _Storage Object Creator_ (para poder subir el código), _Cloud Object Viewer_ (para poder listar el contenido), _Cloud Build Service Account_ (para poder usar dicho servicio) y _Pub/Sub Publisher_ (para poder crear mensajes en una cola de PubSub).

> Google Cloud utiliza Cloud Build y Pub/Sub para hacer determinadas acciones al desplegar un nuevo servicio de App Engine.

* Una llave JSON asociada para impersonarnos en dicha cuenta desde Gitlab.

Podemos ver todos los permisos en la siguiente captura:

![sa-gcp-creation](https://storage.googleapis.com/tangelov-data/images/0024-01.png)

Una vez que tenemos la llave JSON, vamos a Gitlab para que éste lo pueda usar. Vamos a generar tres variables dentro de _Settings_ -- _CI/CD_ -- _Variables_:

* Una de tipo _file_ que contiene el fichero JSON de la cuenta de servicio.

* Dos de tipo _variable_, una con el identificador del proyecto y otra con el nombre de la versión de pruebas.

![variables-cicd](https://storage.googleapis.com/tangelov-data/images/0024-02.png)


#### Despliegue en preproducción
Con el entorno ya preparado, vamos a adecuar nuestro fichero de .gitlab-ci.yml a las nuevas necesidades.

En primer lugar vamos a organizar todos los pasos en _stages_:

* En _build_ vamos a colocar todos los pasos que impliquen la generación del entorno de preproducción.

* En _test_ vamos a integrar todos los pasos que impliquen testeo y validación del servicio y del contenido del blog.

* En _deploy_ vamos a mantener el paso de desplegar el blog contra Docker Hub y vamos a añadir dos acciones extra: el despliegue contra producción y la eliminación del entorno preproductivo.


Vamos a añadir _build_ y a realizar una serie de pasos extra:

* Ahora vamos a definir la imagen base en cada paso, en lugar de hacerlo de forma global, para poder elegir la que queramos en función de nuestras necesidades.

* Definimos un nuevo _job_ llamado _staging-build_ que utilizando los dockers de Nikola y de Google Cloud SDK, genera el HTML estático, carga las credenciales de Gitlab y despliega una nueva versión temporal. 

Nuestro fichero .gitlab-ci.yml ha quedado temporalmente así:

```yaml
services:
  - docker:dind

stages:
  - build
  - deploy

staging-build:
  image: docker:latest
  stage: build
  before_script:
    - docker run --rm -v $PWD:/site -w /site registry.gitlab.com/paddy-hack/nikola nikola build
  script:
     - docker run --name gcloud-config -v /builds/tangelov/tangelov-me.tmp/:/tmp google/cloud-sdk:alpine gcloud auth activate-service-account --key-file='/tmp/GCP_KEY'
     - docker run --rm --volumes-from gcloud-config -v $PWD/output:/root google/cloud-sdk:alpine gcloud app deploy /root --version=$TMP_ROUTE --no-promote --quiet --project=$PROJECT_ID

docker-deploy:
  image: docker:latest
  stage: deploy
  before_script:
    - docker run --rm -v $PWD:/site -w /site registry.gitlab.com/paddy-hack/nikola nikola build
    - docker login -u gitlab-ci-token -p $CI_JOB_TOKEN $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY/tangelov/tangelov-me:latest .
    - docker push $CI_REGISTRY/tangelov/tangelov-me:latest
  rules:
    - if: '$CI_COMMIT_BRANCH == "master"'
```

#### Testing básico
Nuestro _pipeline_ avanza viento en popa y ahora que ya genera un "entorno de pruebas", vamos a implementar algún tipo de testeo que valide que lo que estamos subiendo funciona correctamente.

Este blog es HTML estático: no tiene comentarios, ni funcionalidades complejas, por lo que los tests no van a ser unitarios, sino que van a validar ciertas cosas:
* Que el entorno de pruebas funciona. La manera más sencilla de hacerlo es ver si devuelve un status code 200 a través de su URL.

* Que en caso de que lo desplegado sea un nuevo post, realmente éste está incluido en el código (una vez se me olvidó añadir el fichero xD ). Como Nikola genera un feed RSS, vamos a comparar que el último post del entorno de pruebas y el productivo son diferentes.

Comenzamos creando un nuevo fichero de requerimientos para los test: _requirements-test.txt_ y añadimos las librerías que vamos a utilizar: _pytest_ para lanzar los test, _requests_ para hacer peticiones a alguna URL y _feedparser_ para obtener el contenido de un feed RSS).

También tenemos que picarnos el código de los tests: en este caso he generado un fichero llamado basic\_tests.py en la carpeta _tests_. El código hace exactamente lo descrito arriba: así que cómo [no es la primera vez](https://tangelov.me/posts/ansible-v.html) que publico algún artículo referente a testing en Python, no me voy a enrrollar. Quien tenga curiosidad puede revisar el código de pruebas [aquí](https://gitlab.com/tangelov/tangelov-me/tree/master/tests).

Ya tenemos los tests hechos, así que vamos a generar un nuevo _stage_ en .gitlab-ci.yml:

```yaml
services:
  - docker:dind

stages:
  - build
  - test
  - deploy

[staging-build]

staging-test:
  image: python:3.7-alpine
  stage: test
  script:
    - pip3 install -r requirements-test.txt
    - pytest tests/basic_tests.py

[docker-deploy]
```

#### Pasos finales
El _pipeline_ ya crea un entorno de pruebas, ejecuta algunas acciones de testeo y despliega contra Dockerhub un contenedor. Ahora vamos a añadir un nuevo job dentro del _stage_ de deploy, que despliegue el código en producción y elimine el entorno de pruebas.

También vamos a añadir condicionales a los jobs para que sólo se ejecuten en determinadas circunstancias. Mientras que los dos primeros _stages_ (build y test) se harán siempre en ramas que no sean master, las dos últimas sólo lo harán sobre dicha rama. El código final sería el siguiente:

```yaml
services:
  - docker:dind

stages:
  - build
  - test
  - deploy

staging-build:
  image: docker:latest      
  stage: build
  before_script:
    - docker run --rm -v $PWD:/site -w /site registry.gitlab.com/paddy-hack/nikola nikola build
  script:
     - docker run --name gcloud-config -v /builds/tangelov/tangelov-me.tmp/:/tmp google/cloud-sdk:alpine gcloud auth activate-service-account --key-file='/tmp/GCP_KEY'
     - docker run --rm --volumes-from gcloud-config -v $PWD/output:/root google/cloud-sdk:alpine gcloud app deploy /root --version=$TMP_ROUTE --no-promote --quiet --project=$PROJECT_ID
  rules:
    - if: '$CI_COMMIT_BRANCH != "master"'

staging-test:
  image: python:3.7-alpine
  stage: test
  script:
    - pip3 install -r requirements-test.txt
    - pytest tests/basic_tests.py
  rules:
    - if: '$CI_COMMIT_BRANCH != "master"'

docker-deploy:
  image: docker:latest
  stage: deploy
  before_script:
    - docker run --rm -v $PWD:/site -w /site registry.gitlab.com/paddy-hack/nikola nikola build
    - docker login -u gitlab-ci-token -p $CI_JOB_TOKEN $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY/tangelov/tangelov-me:latest .
    - docker push $CI_REGISTRY/tangelov/tangelov-me:latest
  rules:
    - if: '$CI_COMMIT_BRANCH == "master"'

production-deploy:
  image: docker:latest
  stage: deploy
  before_script:
    - docker run --rm -v $PWD:/site -w /site registry.gitlab.com/paddy-hack/nikola nikola build
  script:
    - docker run --name gcloud-config -v /builds/tangelov/tangelov-me.tmp/:/tmp google/cloud-sdk:alpine gcloud auth activate-service-account --key-file='/tmp/GCP_KEY'
    - docker run --rm --volumes-from gcloud-config -v $PWD/output:/root google/cloud-sdk:alpine gcloud app versions delete $TMP_ROUTE --quiet --project=$PROJECT_ID
    - docker run --rm --volumes-from gcloud-config -v $PWD/output:/root google/cloud-sdk:alpine gcloud app deploy /root --version=master --no-promote --quiet --project=$PROJECT_ID
  rules:
    - if: '$CI_COMMIT_BRANCH == "master"'
```

Ya tenemos nuestro pipeline funcionando, no es perfecto (podría usar dos proyectos para tener un entorno de preproducción real, etc.) pero de momento me vale.

![pipeline-example](https://storage.googleapis.com/tangelov-data/images/0024-03.gif)

Un saludo a todo el mundo y gracias.

## Documentación

* [We're moving from Azure to Google Cloud Platform (ENG)](https://about.gitlab.com/2018/06/25/moving-to-gcp/)

* [New year, new Github: Annuncing unlimited free privare repos and unified Enterprise offering (ENG)](https://github.blog/2019-01-07-new-year-new-github/)

* [Página oficial de Gitea (ENG)](https://gitea.io/en-us/)

* [Sección sobre Git Hooks en la Doc oficial (ENG)](https://git-scm.com/book/pl/v2/Customizing-Git-Git-Hooks)

* [Documentación de Atlassian sobre Git Hoks (ENG)](https://www.atlassian.com/es/git/tutorials/git-hooks)

* [Página sobre de Git Hooks (ENG)](https://githooks.com/)

* [Variables y configuración de Gitlab CI/CD](https://docs.gitlab.com/ee/ci/yaml/)

* [Imagen oficial de Google Cloud SDK en Dockerhub (ENG)](https://hub.docker.com/r/google/cloud-sdk/)

* [Gitlab: Automatically testing your Python project (ENG)](https://cylab.be/blog/18/gitlab-automatically-testing-your-python-project)


Revisado a 01/04/2023

---
title: "Integración continua con Gitlab (I): primeros pasos"
slug: ic-gitlab
authors:
  - tangelov
date: 2018-08-10T07:00:00+02:00
tags:  ["devops", "gitlab", "ci"]
categories: ["devops"]
draft: false
---

Yo utilizo Gitlab desde hace tiempo. Los códigos de ejemplo que pongo en este blog están almacenados allí. En este post, voy a explicar cómo utilizar sus herramientas de integración continua, pero primero... ¿Qué es Gitlab?

Gitlab es un sistema de gestión de repositorios de git, de código abierto. Es un sistema escrito en Ruby que además de permitir gestionar código a través de un navegador, tiene muchísimas herramientas integradas en él. Algunas de estas herramientas permiten manejar nuestro código, compilarlo y realizarle diferentes acciones y pruebas al resultado. Si estas acciones se realizan de forma ágil podríamos decir que estamos usando integración continua.

Aunque podemos instalarlo en nuestro propio servidor, la versión en la nube de [Gitlab](https://gitlab.com/users/sign_in) nos permite disfrutar de él.

<!--more-->

## Introducción a CI en Gitlab
Cuando entramos en un repositorio de código en Gitlab, una de las opciones que tenemos en el panel de la izquierda es _CI/CD_, es decir _continuous integration / continuos delivery_

![cicd](https://storage.googleapis.com/tangelov-data/images/0012-00.png)

Si hacemos click en _Get started with Pipelines_ se nos abrirá un [tutorial](https://docs.gitlab.com/ee/ci/quick_start/index.html) que podremos seguir para configurar nuestro sistema de CI. No voy a entrar en profundidad en el tutorial y sólo comentaré que para activarlo necesitamos crear en la raíz de nuestro repositorio un fichero llamado _gitlab-ci.yml_

![cicd-error](https://storage.googleapis.com/tangelov-data/images/0012-01.png)

Si ahora volvemos a entrar en el mismo lugar, veremos un error pero ya podremos empezar a jugar. La idea de éste post es coger el código, compilarlo, generar un paquete para desplegarlo en un contenedor de Nginx y subir éste a un Registry de Docker.

## Creación del HTML
Los primeros pasos que debemos dar para lograr nuestro objetivo es descargarnos el código, compilarlo y generar el HTML con nikola. Si lo hicieramos en una máquina nueva, haríamos lo siguiente:

```bash
sudo apt-get update && sudo install python3-pip -y
pip3 install nikola[extras]
git clone https://gitlab.com/tangelov/tangelov-me
cd tangelov-me && nikola build
```

Con los pasos anteriores, tendríamos nuestro HTML generado y podríamos subirlo a cualquier servidor web. Sin embargo, vamos a darle una vuelta extra y vamos a encapsularlo dentro de un contenedor con Nginx. Para ello creamos un archivo _Dockerfile_ en la raíz del repositorio (si, la mayúscula es importante):

```Dockerfile
FROM nginx:stable-alpine

COPY output /usr/share/nginx/html
```

Lo único que hace este fichero es coger un servidor Nginx encapsulado y añadirle el código HTML que hemos generado en el paso anterior.


## Nuestro primero pipeline
Nuestro objetivo ahora es crear un proceso que nos genere todo el proceso anterior. Necesitamos que se instale Nikola y Docker: el primero para generar el HTML y el segundo para generar la imagen con el Nginx. Vamos al lío:

```yml
image: ubuntu:18.04

stages:
  - build

ubuntu-build:
  stage: build
  script:
    - apt-get update -y
    - apt-get install python3-pip docker.io -y
    - service docker start
    - pip3 install nikola[extras]
    - nikola build
    - docker build -t $CI_REGISTRY/tangelov/tangelov-me:ubuntu .
    - docker login -u gitlab-ci-token -p $CI_JOB_TOKEN $CI_REGISTRY
    - docker push $CI_REGISTRY/tangelov/tangelov-me:ubuntu
```

Nuestro fichero consta de diferentes partes:

* _image_: se corresponde a la imagen de Docker que va a contener todo el proceso de creación y empaquetado del contenedor.

* _stages_: nos permiten organizar los diferentes jobs que hagamos. Los que tengan el mismo _stage_ se ejecutan a simultáneamente y los que no en orden:

* _ubuntu-build_: contiene todos los pasos que necesitamos para generar nuestra imagen. Como podemos ver, se realizan los mismos pasos que si fuera nuestro PC añadiendo tres pasos que se tiran con el comando docker (generación de la imagen en local, autorización en el registro de Gitlab y envío de dicha imagen. Las variables $CI\_REGISTRY y $CI\_JOB\_TOKEN son una serie de variables internas que Gitlab inyecta en el job para facilitarnos la vida. Podemos obtener más información al respecto [aquí](https://docs.gitlab.com/ee/ci/variables/)

Ahora hacemos push contra una rama y se lanzará un job:

![cicd-ubuntu](https://storage.googleapis.com/tangelov-data/images/0012-02.png)


## Rizando el rizo
Como podemos ver, el job ha tardado unos 3 minutos en realizarse. Este proceso se puede mejorar mucho y es lo que vamos a hacer. En primer lugar, vamos a cambiar la imagen a utilizar y vamos a utilizar imágenes basadas en Alpine Linux (mucho más pequeñas) y que ya contienen Docker. 

```yml
image: docker:latest

services:
  - docker:dind

stages:
  - build
```

Mientras que la _docker:latest_ se corresponderá con el cliente, la imagen que se encuentra en services, _docker:dind_ es una imagen que contiene el demonio y es accesible desde otras imágenes. Entonces ahora sólo necesitamos una imagen que contenga nikola. Voy a utilizar una de [Olaf Meeuwissen](https://gitlab.com/paddy-hack/nikola/container_registry) que también está en Gitlab para generar el código. Nuestro .gitlab-ci.yml es actualmente así:

```yml
image: docker:latest

services:
  - docker:dind

stages:
  - build

alpine-build:
  stage: build
  script:
    - docker run --rm -v $PWD:/site -w /site -u $(id -u):$(id -g) registry.gitlab.com/paddy-hack/nikola nikola build
    - docker build -t $CI_REGISTRY/tangelov/tangelov-me:alpine .
    - docker login -u gitlab-ci-token -p $CI_JOB_TOKEN $CI_REGISTRY
    - docker push $CI_REGISTRY/tangelov/tangelov-me:alpine
```

Sin embargo, vamos a retocarlo un poquito más. Vamos a hacer que nuestro código sólo se ejecute cuando se trabaje en master y a simplificar un poco los comandos. Así queda definitivamente:

```yml
image: docker:latest

services:
  - docker:dind

stages:
  - build

alpine-build:
  stage: build
  before_script:
    - docker run --rm -v $PWD:/site -w /site registry.gitlab.com/paddy-hack/nikola nikola build
    - docker login -u gitlab-ci-token -p $CI_JOB_TOKEN $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY/tangelov/tangelov-me:alpine .
    - docker push $CI_REGISTRY/tangelov/tangelov-me:alpine
  only:
    - master
```

Esta vez no se ha producido nada de manera automática porque no estamos trabajando en master. Hacemos un merge request y lo aprobamos para que se cumpla:

![cicd-alpine](https://storage.googleapis.com/tangelov-data/images/0012-03.png)

Como podemos ver, ahora tenemos un job que se nos crea una imagen de Docker de forma automática, cada vez que hagamos algo en master y que ha tardado poco más de la mitad que en el caso anterior. Pues hasta aquí el post de hoy. Espero que haya gustado.


## Documentación

* [Página de Gitlab en la Wikipedia (ENG)](https://en.wikipedia.org/wiki/GitLab)

* [Definición de Integración Continua en la Wikipedia (ENG)](https://en.wikipedia.org/wiki/GitLab)

* [Introducción a la Integración continua en Gitlab (ENG)](https://about.gitlab.com/stages-devops-lifecycle/continuous-integration/)

* [Documentación sobre cómo configurar gitlab-ci (ENG)](https://docs.gitlab.com/ee/ci/yaml/)

* [Test all the things in GitLab CI with Docker by example (ENG)](https://about.gitlab.com/2018/02/05/test-all-the-things-gitlab-ci-docker-examples/)


Revisado a 01/03/2021

---
title: "Integración continua con Github: Travis CI"
slug: ic-github
authors:
  - tangelov
date: 2018-09-20T05:00:00+02:00
tags:  ["devops", "github, ci"]
categories: ["devops"]
draft: false
---

Github es uno de los servicios más importantes que existen en este momento en el mundo del desarrollo de software. Pese a haber sido recientemente adquirido por Microsoft, sigue siendo la plataforma de gestión de repositorios más usada del mundo.

Como ya comenté [hace tiempo](http://tangelov.me/posts/ic-gitlab.html), utilizo personalmente Gitlab como sistema de repositorios de código fuente, pero la verdad es que estaba deseando probar "su" sistema de integración continua, llamado [Travis CI](https://travis-ci.org/).

> Travis CI ha cambiado sus políticas de uso y ahora no es el sistema principal de integración continua para Github. Aunque sigue funcionando, ahora recomendaría el uso de [Github Actions](https://github.com/features/actions), pero mantengo este post activo por si a alguien le puede resultar de ayuda. Para más información sobre las nuevas políticas de uso de Travis CI, recomiendo [el post](https://www.jeffgeerling.com/blog/2020/travis-cis-new-pricing-plan-threw-wrench-my-open-source-works) de Jeff Geerling al respecto.

<!--more-->

## Primeros pasos
Para comenzar a utilizar Github y Travis CI, primero debemos [registrarnos](https://github.com/join?return_to=%2Fjoin%3Fsource%3Dheader-home&source=login). Una vez que ya estamos dentro, nuestro siguiente paso es crear un repositorio y dotarle de contenido.

En este caso he decidido, crear un repositorio espejo que utilice como fuente, el desarrollo de este blog en Gitlab. Tras crear dicho repositorio en Github, Se tarda menos de cinco minutos en hacer siguiendo [estas instrucciones](https://docs.gitlab.com/ee/workflow/repository_mirroring.html#setting-up-a-push-mirror-from-gitlab-to-github)

Si ahora nos metemos en nuestra cuenta de Github, veremos el código de nuestro repo:

![tangelov-en-github](https://storage.googleapis.com/tangelov-data/images/0015-00.png)

## Travis CI
Travis CI es un servicio de integración continua de código abierto ajeno a Github, pero hospedado en él y que proporciona dicho servicio de manera gratuita a todos los proyectos de código abierto que se deseen.

Lo primero que debemos hacer, es dar permisos a Travis CI para poder realizar las builds. Al loguearnos en su web con nuestro usuario de Github, nos pedirán permisos.

![login-travis-ci](https://storage.googleapis.com/tangelov-data/images/0015-01.png)

Al igual que en el caso del CI de Gitlab, debemos crear un fichero oculto que será el encargado de gestionar nuestras builds. La idea general de este post es replicar con otro sistema el resultado obtenido en el anterior post. En este caso el fichero que queremos generar se llamará _.travis.yml_.

### Creamos el fichero
Nuestros primeros pasos deberían ser que se clonase el código, instalase nikola y generase el HTML estático que necesitamos.

```yaml
dist: trusty
sudo: required

language: python
python:
  - "3.6"

before_install:
- pip install -r requirements.txt

script:
  - nikola build
```

Vamos a explicar un poco que significa ese fichero:

* _dist_ se corresponde con la distribución con la que se va a lanzar nuestra build. En este caso hemos elegido Ubuntu Trusty. En este [link](https://docs.travis-ci.com/user/reference/overview/) se pueden ver todos los disponibles. Añadimos _sudo: required_ para poder utilizar Docker en un futuro.

* _language_ se corresponde con el lenguaje de programación utilizado. En este caso vamos a usar Nikola y por eso especificamos _python_ en su versión 3.6.

* _before install_ se encarga de ejecutar una serie de pasos antes de realizar nada. Lo utilizo para instalar las dependencias del proyecto localizadas en el fichero requirements.txt.

* _script_ ejecuta una serie de órdenes que nosotros le pasamos.


Aquí podemos ver el resultado de nuestro proceso:

![travis-ci-result](https://storage.googleapis.com/tangelov-data/images/0015-02.png)

### Añadimos docker a .travis.yml
Nuestra build ya se descarga el código y genera el código HTML resultante, pero ahora vamos a añadir algunos pasos más.

```yaml
dist: trusty
sudo: required

services: docker

language: python
python:
  - "3.6"

before_install:
- pip install -r requirements.txt

script:
  - nikola build
  - echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USER" --password-stdin
  - docker build -t $DOCKER_USER/tangelov-me:latest .
  - docker push $DOCKER_USER/tangelov-me:latest
```

Hemos añadido el servicio de docker al fichero, que hace que podamos utilizar los comandos de Docker y tres pasos más que nos loguean en Dockerhub, crean y pushean la imagen a dicho repositorio.

Sin embargo, primero debemos añadir las variables de entorno para que Travis pueda gestionar las credenciales de Docker, en Settings:

![travis-ci-conf](https://storage.googleapis.com/tangelov-data/images/0015-03.png)

Una vez realizado esto podemos ejecutar nuestro job y ver que el resultado es satisfactorio. En Dockerhub se ha creado una nueva imagen totalmente funcional:

![dockerhub-result](https://storage.googleapis.com/tangelov-data/images/0015-04.png)

### Configuraciones extra
En el estado actual de las cosas, cualquier push que se haga al repositorio provocará que se lance el job. Como nuestra idea es simular lo que tenemos en Gitlab, en este nuevo entorno, vamos a limitar que sólo ocurra cuando se realicen merges contra la rama principal.

Tan sólo debemos añadir una lista blanca con la rama principal:

```yaml
dist: trusty
sudo: required

services: docker

language: python
python:
  - "3.6"

branches:
  only:
    - master

before_install:
- pip install -r requirements.txt

script:
  - nikola build
  - echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USER" --password-stdin
  - docker build -t $DOCKER_USER/tangelov-me:latest .
  - docker push $DOCKER_USER/tangelov-me:latest
```

Y listo :D


## Documentación

* [Primeros pasos con Travis CI (ENG)](https://docs.travis-ci.com/user/getting-started/)

* [Configuración de Travis CI para usar Docker (ENG)](https://docs.travis-ci.com/user/docker/)

* [Paso a paso con los pipelines de Travis CI (ENG)](https://docs.travis-ci.com/user/customizing-the-build/)

* [Sobre el entorno Bionic en Travis CI (ENG)](https://docs.travis-ci.com/user/reference/bionic/)

* [Introducción a la Integración continua en Gitlab (ENG)](https://about.gitlab.com/product/continuous-integration/)

Revisado a 01/03/2021

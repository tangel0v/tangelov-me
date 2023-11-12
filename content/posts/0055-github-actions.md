---
title: "Integración continua con Github II: Github Actions"
slug: ic-github-ii
authors:
  - tangelov
date: 2023-11-12T08:00:00+02:00
tags:  ["devops", "github", "ci"]
categories: ["devops"]
draft: false
---

La mayoría de plataformas como Github o Gitlab (también llamadas forjas de código, aunque a mi no me gusta mucho como suena), no han parado de implementar nuevas funcionalidades, tratando de convencer al público de que son la mejor herramienta para la creación de nuevas aplicaciones.

Hace años, casi todos los proyectos Open Source alojados en Github, utilizaban Travis CI para ejecutar sus pipelines de CICD. Sin embargo, a finales de 2020, dicha plazaforma  [cambió sus condiciones]((https://blog.travis-ci.com/2020-11-02-travis-ci-new-billing)) y muchos de sus usuarios tuvieron que buscar otra alternativa.

La simbiosis entre plataformas no era oficial y tras un tiempo, Github presentó su propia solución: _Github Actions_. En este post, busco actualizar una [antigua entrada](https://tangelov.me/posts/ic-github.html) que escribí sobre Travis CI y replicar las funcionalidades de dicho pipeline pero sobre Actions. Pero primero, un poco de historia.

<!--more-->

## Github y Microsoft
Uno de los bombazos del 2018 fue la compra de Github por Microsoft por aproximadamente 7000 millones de dólares. Dicha compra rivalizaba con alguno de los productos que ellos ya comercializaban (Team Fundations Server o Azure DevOps) y parte de la comunidad pensaba que alguno de ellos terminaría siendo abandonado. Sin embargo, la evolución de ambos ha sido constante y podemos utilizar cualquiera de ellos para crear pipelines complejas, según nuestras necesidades.

## Github Actions
Github Actions es una plataforma que permite la ejecución de tareas cuando ocurren ciertos eventos sobre nuestro código. Algunos eventos pueden ser "realizar un commit sobre determinadas ramas" o "fusionar distintas ramas de código", etc.

Los pipelines que definimos en Github Actions reciben el nombre de _workflows_ y podemos crear todos los que queramos según nuestas necesidades.

Utilizar Github Actions requiere contratar algún plan de uso, pero si queremos probarlo, su tier gratuito es muy generoso y nos cubre hasta 2000 minutos de ejecuciones cada mes sin coste alguno.

Si queremos utilizar esta plataforma de pipelines, lo primero que necesitamos es una cuenta y un repositorio en Github. Aunque existen [formas de utilizarlas en otras plataformas](https://tomasvotruba.com/blog/how-can-we-use-github-actions-in-gitlab/), yo matengo un mirroring entre Github y Gitlab para mi blog y puedo usar los servicios de Github si lo necesito.

![blog-integrations-2022](https://storage.googleapis.com/tangelov-data/images/0037-00.png)

Este diagrama describe el estado actual de las integraciones de mi blog. Cuando realizo un cambio sobre mi repositorio de Gitlab, éste se replica automáticamente hacia Github y se ejecutan una serie de operaciones en Gitlab CI que testean el código, crean un contenedor y despliegan el contenido del repositorio en su destino.

Gracias al _mirroring_ con Github, anteriormente había un pipeline que se ejecutaba en Travis CI y creaba una imagen pública para después subirla a DockerHub. Sin embargo, esta parte no funciona desde que Travis CI cambió sus condiciones de uso y que vamos a solucionar ahora mismo.

Tras esta introducción, ya podemos ponernos manos a la obra.


### Primeros pasos
Github Actions no pretende reinventar la rueda, y al igual que otras plataformas de CICD, se basa en ficheros YAML, con una estructura donde definimos que acciones queremos ejecutar y cuando hacerlo. En este caso, tan sólo necesitamos crear una carpeta de nombre _.github/workloads_ en la raíz de nuestro repositorio y dentro de ella, uno o más ficheros con extensión _.yaml_.

Cada fichero .yaml creado genera un workflow distinto y su estructura puede complicarse bastante, así que antes de crear el nuestro, voy a explicarla un poco basándome en el ejemplo que Github proporciona en el siguiente [link](https://docs.github.com/en/actions/quickstart):


```yaml
name: GitHub Actions Demo
run-name: ${{ github.actor }} is testing out GitHub Actions 🚀
on: [push]
jobs:
  Explore-GitHub-Actions:
    runs-on: ubuntu-latest
    steps:
      - run: echo "🎉 The job was automatically triggered by a ${{ github.event_name }} event."
      - run: echo "🐧 This job is now running on a ${{ runner.os }} server hosted by GitHub!"
      - run: echo "🔎 The name of your branch is ${{ github.ref }} and your repository is ${{ github.repository }}."
      - name: Check out repository code
        uses: actions/checkout@v4
      - run: echo "💡 The ${{ github.repository }} repository has been cloned to the runner."
      - run: echo "🖥️ The workflow is now ready to test your code on the runner."
      - name: List files in the repository
        run: |
          ls ${{ github.workspace }}
      - run: echo "🍏 This job's status is ${{ job.status }}."
```

En general podemos decir que cada workflow se compone de tres _objetos_:
* __name__ es el nombre que nuestro workflow va a tener y a mostrar dentro de la interfaz de Github Actions.
* __on__ se corresponde con el _cuando_ se va a ejecutar nuestro workflow. Aquí definimos los eventos que van a disparar su ejecución.
* __jobs__ son la lista de pasos que nuestro workflow va a ejecutar cada vez.

En este caso, estamos creando un workflow de nombre _Github Actions Demo_, que se ejecuta cada vez que hagamos un _push_ al repositorio y que ejecuta un job llamado _Explore-Github_Actions_.

A su vez, cada job tiene una serie de palabras clave con su propia nomenclatura y estructura:
* __runs-on__ define la imagen donde queremos que nuestro workflow se ejecute. Puede ser un ejecutor público o privado en función de nuestas necesidades. En este caso está utilizando el ejecutor público llamado _ubuntu-latest_.
* __steps__ define uno a uno y de forma secuencial, los procesos nuestro workflow va a ejecutar.

Este workflow es muy sencillo:
* Primero imprime una serie de lineas por la pantalla utilizando como plantilla algunos de las variables que Github toma del contexto del repositorio como el tipo de evento, el nombre del repositorio o la rama del mismo, etc. __Run__ nos permite ejecutar comandos sueltos como si de una terminal se tratase.
* En segundo lugar reutiliza la Github Action de nombre _actions/checkout_ en su versión 4 (en breve hablaremos de esto) para copiar la versión del código definida en __on__ gracias a la directiva __uses__.
* Por último, nos lista los ficheros que hay en esta revisión del código y si todo es correcto, nos indica que la ejecución del código ha funcionado.

### Definiendo los diferentes steps
Una de las ventajas de utilizar Github Actions es la inmensa comunidad que hay detrás y lo fácil que es reutilizar acciones que otros usuarios hayan hecho. Esto hace que portar la funcionalidad de mi pipeline en Travis CI sea muy sencillo y no tenga que mantener prácticamente código propio.

![github-actions-diagram](https://storage.googleapis.com/tangelov-data/images/0055-00.png)

El proceso de generación de la imagen del contenedor sólo consta de dos pasos:
* En el primero, utilizamos Hugo para generar el HTML definitivo.
* En el segundo, utilizamos dicho código HTML y el Dockerfile almacenado en el repositorio para crear la imagen, etiquetarla y subirla a DockerHub.

El primer paso es definir el workflow y cuando se va a ejecutar. En mi caso, quiero que se ejecute cuando se realiza un push o un merge a _master_ o _main_ y que su nombre sea "Tangelov GH Actions To DockerHub".

```yaml
name: Tangelov GH Actions To DockerHub
on: 
  push:
    branches:
      - 'master'
      - 'main'
```

Ahora podemos proceder a definir los distintos pasos de nuestro workflow:

```yaml
jobs:
  docker-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository code
        uses: actions/checkout@v4

      - name: Setup Hugo in Github Actions
        uses: peaceiris/actions-hugo@v2

      - name: Build Hugo static content
        run: hugo --minify

      - name: Save output for next steps
        uses: actions/cache@v2
        with:
          path: public
          key: public
```

Para crear el código, vamos a utilizar distintas _Actions_ mantenidas por la comunidad:
* Primero nos descargamos el código utilizando la acción _actions/checkout_ en su versión 4.
* Después utilizamos la acción _actions-hugo_ del usuario _peaceiris_ en su versión 2 y ejecutamos el comando ```hugo --minify``` para generar el código HTML.
* Por último, guardamos la carpeta _public_ dentro de la caché para que otros pasos posteriores puedan utilizarla.

En este punto ya podríamos crear la imagen del contenedor y subirla a DockerHub, pero antes, necesitamos hacer que Github pueda acceder a DockerHub. Para ello, necesitamos generar un token de acceso y almacenarlo en Github Actions.

Crear el token es sencillo y tan sólo tenemos que ir a nuestra cuenta y hacer click aquí:

![create-docker-token](https://storage.googleapis.com/tangelov-data/images/0055-01.png)

Una vez tenemos nuestro token, ahora necesitamos crear dos variables en Github, una llamada _DOCKER\_USER_ y otra _DOCKER\_PASSWORD_ con el token creado en el paso anterior.

![docker-creds-github](https://storage.googleapis.com/tangelov-data/images/0055-02.png)

Ahora ya podemos proceder a crear el código de los siguientes pasos:

```yaml
      - name: Docker Login using Github Action
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USER }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Docker Build and Push using Github Action
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_USER }}/tangelov-me:latest

```

Cuando reutilizamos una _Action_, ésta puede ser configurada a través de variables. En este caso estamos utilizando _docker/login-action_ y le estamos indicando que tiene que obtener el valor de dichas variables del almacen de secretos de Github, buscando las variables _DOCKER\_USER_ y _DOCKER\_PASSWORD_ que acabamos de definir. Este "contexto" se le pasa a través de la directiva __with__.

El resto de pasos nos permiten construir, etiquetar y almacenar nuestra imagen en DockerHub.

Llegados a este punto, ya tendríamos un pipeline completo y funcional, pero... ¿Y si le añadimos alguna funcionalidad extra?

Tener trazabilidad en nuestro código es importante. Nos permite saber que paquetes o aplicaciones han sido construidas a partir de una versión del código concreta y en base a nuestros tests o resultados, dar marcha atrás si encontramos algún bug o error. Aunque en este caso no es muy útil puesto que el "código" es sólo HTML, espero que este ejemplo sirva como ejemplo para otros.

A nuestro pipeline, vamos a añadirle el uso del identificador SHA de nuestro commit para etiquetar cada una de las imágenes Docker que hemos creado:

```yaml
      - name: Set short git commit SHA
        run: |
          calculatedSha=$(git rev-parse --short ${{ github.sha }})
          echo "COMMIT_SHORT_SHA=$calculatedSha" >> $GITHUB_ENV

      - name: Docker Build and Push using Github Action
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: | 
            ${{ secrets.DOCKER_USER }}/tangelov-me:latest
            ${{ secrets.DOCKER_USER }}/tangelov-me:${{ env.COMMIT_SHORT_SHA }}
```

Por defecto, Github no nos proporciona el SHA "corto" de Git, así que vamos a generarlo usando comandos de git y a generar una nueva variable de entorno llamada _COMMIT\_SHORT\_SHA_. Después, lo añadimos como tag en el paso de construir y enviar el contenedor a DockerHub.

El resultado final sería el siguiente:

```yaml
name: Tangelov GH Actions To DockerHub
on: 
  push:
    branches:
      - 'main'
      - 'master'

jobs:
  docker-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository code
        uses: actions/checkout@v4

      - name: Set short git commit SHA
        run: |
          calculatedSha=$(git rev-parse --short ${{ github.sha }})
          echo "COMMIT_SHORT_SHA=$calculatedSha" >> $GITHUB_ENV

      - name: Setup Hugo in Github Actions
        uses: peaceiris/actions-hugo@v2

      - name: Build Hugo static content
        run: hugo --minify

      - name: Save output for next steps
        uses: actions/cache@v2
        with:
          path: public
          key: public

      - name: Docker Login using Github Action
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USER }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Docker Build and Push using Github Action
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: | 
            ${{ secrets.DOCKER_USER }}/tangelov-me:latest
            ${{ secrets.DOCKER_USER }}/tangelov-me:${{ env.COMMIT_SHORT_SHA }}
```

Et voilá:

![docker-github-action](https://storage.googleapis.com/tangelov-data/images/0055-03.png)

![dockerhub-final](https://storage.googleapis.com/tangelov-data/images/0055-04.png)


## Conclusión
Github Actions es una plataforma de CICD completa, que no tiene nada que envidiarle a su competencia, que además se beneficia de una inmensa comunidad y popularidad y que facilita la reutilización de código. En puntos donde puede quedarse un poco coja, la comunidad ha tomado el testigo ampliando sus funcionalidades hasta el infinito.

Tiene integraciones nativas con gran cantidad de proveedores de nube y el único motivo que tengo para no recomendarla serían sus [incidencias técnicas](https://www.githubstatus.com/history), pero espero que su cadencia se vaya reduciendo a medida que el producto esté más pulido.

Así que me despido y espero que este post os sea útil, ¡Happy Coding!


## Documentación

* [Official page of Azure DevOps Server (ENG)](https://azure.microsoft.com/es-es/services/devops/server/)

* [Azure DevOps Pipelines vs Github Actions](https://docs.microsoft.com/en-us/dotnet/architecture/devops-for-aspnet-developers/actions-vs-pipelines)

* [GitHub Actions quickstart (ENG)](https://docs.github.com/en/actions/quickstart)

* [Github Workflow Syntax (ENG)](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

* [Create short SHA for tagging Docker images (ENG)](https://dev.to/hectorleiva/github-actions-and-creating-a-short-sha-hash-8b7)

* [Act, execute Github Actions locally (ENG)](https://github.com/nektos/act)


Revisado a 12-11-2022

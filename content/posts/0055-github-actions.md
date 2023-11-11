---
title: "Integración continua con Github II: Github Actions"
slug: ic-github-ii
authors:
  - tangelov
date: 2023-12-10T08:00:00+02:00
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
Una vez que nuestro repositorio ya está creado, necesitamos crear una carpeta de nombre _.github/workloads_ y en ella uno o más ficheros con extensión _.yaml_ para comenzar a utilizar Github Actions.

La estructura del fichero YAML merece alguna explicación y para ello vamos a utilizar el ejemplo que nos proporciona Github en el siguiente [link](https://docs.github.com/en/actions/quickstart):

Cada fichero .yaml que creamos se corresponde con un workflow distinto y tienen la siguiente estructura:

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

Vamos a explicar un poco la estructura del YAML:
* __name__ se corresponde con el nombre que nuestro Workflow va a tener en la interfaz de Github.
* __on__ te permite definir ante que eventos se ejecutará nuestra pipeline. También podemos ejecutarlo de forma manual si queremos.
* __jobs__ te permite definir cada uno de los pasos que vamos a ejecutar en nuestro pipeline y tiene una estructura propia.

Cada job tiene a su vez su propia estructura:
* __runs-on__ define donde queremos que se ejecute ya sea un ejecutor compartido o uno privado, dependiendo de nuestas necesidades.
* __uses__ define el origen de otro workflow reutilizable (luego hablaremos de esto).
* __with__ define variables que vamos a utilizar en workflows reusables.
* __steps__ define los pasos que tiene cada job y que comando se va a ejecutar en dicho paso.


### Definiendo los diferentes steps
El proceso que tenemos que crear en Github Actions consta de dos pasos:
* En un primer paso, tenemos que utilizar Hugo para generar el HTML final que contendrá el contenedor.
* En el siguiente paso, utilizaremos un fichero Dockerfile para generar el contenedor y subirlo a DockerHub.

Primero tenemos que definir el nombre de nuestro Workflow y sobre qué eventos se va a ejecutar. En este caso, solo quiero que se cree un contenedor cuando se mergee una rama a _master_:

```yaml
name: Tangelov GH Actions To DockerHub
on: 
  push:
    branches:
      - 'master'
```

En segundo lugar, tenemos que definir los pasos que necesitamos para generar el HTML que utilizamos en el contenedor:
1. Reutilizamos la action _checkout_ para coger la última versión disponible del código en dicha rama.
2. Después reutilizamos la action _actions-hubo_ de peaceiris para generar el código.
3. Por último, salvamos el output del proceso para poder utilizarlo en pasos futuros.

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

El último paso va a crear el contenedor, lo va a etiquetar correctamente y lo va a subir a Dockerhub. Para ello, primero necesitamos crear un token y guardar su contenido en Github Actions.

Para crear el token, nos vamos a nuestra cuenta y hacemos click aquí:

![create-docker-token](https://storage.googleapis.com/tangelov-data/images/0055-00.png)

Una vez tenemos nuestro token, vamos a crear dos variables, una llamada _DOCKER\_USER_ y otra _DOCKER\_PASSWORD_ con el token creado en el paso anterior.


![docker-creds-github](https://storage.googleapis.com/tangelov-data/images/0055-01.png)

Por último, tenemos que crear el paso que nos genere el contenedor y nos lo suba a Dockerhub. Para este paso vamos a utilizar los steps creados y mantenidos por Docker directamente:

```yaml
      - name: Docker Login using Github Action
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USER }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Docker Build and SHA Push using Github Action
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_USER }}/tangelov-me:latest

      - name: Docker Build and Push using Github Action
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_USER }}/tangelov-me:latest

```


## Documentación

* [Official page of Azure DevOps Server (ENG)](https://azure.microsoft.com/es-es/services/devops/server/)

* [Azure DevOps Pipelines vs Github Actions](https://docs.microsoft.com/en-us/dotnet/architecture/devops-for-aspnet-developers/actions-vs-pipelines)

* [GitHub Actions quickstart (ENG)](https://docs.github.com/en/actions/quickstart)

* [Github Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)


Revisado a 11-11-2022

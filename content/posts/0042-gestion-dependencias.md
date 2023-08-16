---
title: "Gestionando dependencias con Renovate"
slug: gestion-de-dependencias
authors:
  - tangelov
date: 2021-05-21T22:00:00+02:00
tags:  ["devops", "functions"]
categories: ["devops", "cloud"]
draft: false
---

Hoy se cumplen diez años del ataque informático que sufrió RSA. Dicha empresaba se dedicaba (y dedica) a crear dispositivos para verificar y proporcionar autenticación en dos pasos a aplicaciones y servicios (como [Yubico](https://tangelov.me/posts/seguridad-nube.html)).

Los atacantes obtuvieron las semillas que la empresa usaba para generar sus productos y las utilizó para atacar a terceros. Este tipo de ataques, que atacan a intermediarios para acceder a los datos de clientes finales, son conocidos con el nombre de ataques de cadena de suministro (_Supply Chain attacks_).

Aunque un ataque puede aprovechar vulnerabilidades no conocidas, la mayoría son conocidas y se ejecutan sobre sistemas desactualizados con falta de mantenimiento. La mejor manera de evitarlos es mantener nuestros sistemas actualizados tan pronto como sea posible.

Cada sistema operativo recibe parches regularmente que nosotros sólo debemos aplicar, pero si somos desarrolladores, los encargados de verificar que nuestra aplicación es segura somos nosotros. Puesto que a medida que nuestra aplicación crece, el número de dependencias se dispara, ¿cómo podemos seguir las actualizaciones de nuestras dependencias de forma eficiente?

<!--more-->


## Introducción
Dentro de la nube pública existe lo que se llama _modelo de responsabilidad compartida_. En él, el proveedor se encarga del buen funcionamiento y la seguridad del software y los servicos que nos ofrece y nosotros de la seguridad y disponibilidad de las aplicaciones desplegadas sobre el proveedor.


Por ello, desde que comencé el blog, siempre he tratado de gestionar las actualizaciones de las librerías y aplicaciones que utilizo:

* Al inicio todo era manual. Anotaba en una lista las cinco o diez dependencias y las verificaba y actualizaba a mano.

* A los pocos meses cambié el sistema por el aumento de dependencias. Cree un grupo en mi RSS donde se registraban las actualizaciones de las aplicaciones y librerías utilizadas. El proceso de añadir una nueva se hacía a mano y así pasaba a estar controlada.

* Durante dos años este sistema funcionó, pero cuando empecé a programar el sistema requirió demasiado mantenimiento y decidí investigar si había mejores formas de gestionar esto.

Buscando herramientas que me permitieran gestionar mejor este problema encontre dos alternativas muy interesantes:

* __Dependabot__: este servicio SaaS te permite seguir las actualizaciones de tus dependencias y crea automáticamente Pull Requests en tus repositorios cuando es necesario. Sin embargo, no es de código abierto y sólo funciona con Github.

* __Renovate__: este proyecto de código abierto, también en formato SaaS, es un servicio similar a Dependabot pero en multiplataforma (soporta Gitlab, Bitbucket, Azure DevOps, Gitea, etc). Permite mucha flexibilidad y lenguajes como Java, Javascript, Python, Go, PHP o Docker. Es justo lo que necesitaba.


## Renovate
Renovate es un proyecto de código abierto, desarrollado por White Source Software, que nos permite analizar el estado de las dependencias de nuestras aplicaciones para mantenerlas actualizadas. Aunque ofrecen una versión en SaaS, también es posible ejecutarlo de forma regular utilizando Docker, proporcionando una gran versatilidad.

En este post, vamos a ver cómo configurar y usar Renovate para validar las dependencias de las funciones que tengo desplegadas en la nube.

#### _Instalando_ Renovate en Gitlab
Para utilizar Renovate en Gitlab tenemos dos opciones: o instalamos y mantenemos el servicio o utilizamos el runner propio que White Source mantiene. En mi caso, la segunda opción es la elegida debido a su sencillez.

Siguiendo el [paso a paso](https://gitlab.com/renovate-bot/renovate-runner/-/blob/main/README.md) que se provee, esto es lo que debemos hacer.

Primero tenemos que crear un nuevo proyecto para hospedar nuestro propio runner. Dicho proyecto puede ser creado en nuestro usuario o crear uno nuevo. En cualquier caso, este usuario será el encargado de abrir los _Merge Requests_ con las actualizaciones de dependencias en los repositorios.

![renovate-project](https://storage.googleapis.com/tangelov-data/images/0042-00.png)

Tras crear el proyecto, ahora debemos darle permisos de _Owner_ o _Maintainer_ al usuario del bot y crear las credenciales necesarias para que éste pueda comunicarse con la API:

* Creamos un token del usuario de Gitlab con los scopes _read\_user_, _api_ y _write\_repository_. 

* Renovate utiliza Github para buscar actualizaciones en Github. Para evitar los límites de la API de Github, recomiendan crear un token en una cuenta de Github, con permisos de sólo lectura (permisos de _public\_repo_, _repo:status_, _repo_deployment_, _repo:invite_ y todos los _read_ que veamos).

Tras crear el usuario (si aplica) y un repositorio, podemos empezar a configurar la aplicación.

Comenzamos añadiendo al repositorio del bot un fichero de nombre _.gitlab-ci.yml_ con el siguiente contenido:

```yaml
include:
  - project: 'renovate-bot/renovate-runner'
    file: '/templates/renovate-dind.gitlab-ci.yml'

renovate:
  only:
    - schedules
```

Este fichero le indica al runner que debe ejecutarse sólo de forma programada, utilizando las plantillas y el [código original](https://gitlab.com/renovate-bot/renovate-runner) del runner que White Source Software mantiene.

Ahora debemos crear una serie de variables de entorno en nuestro repositorio para configurar la herramienta:

* _RENOVATE\_TOKEN_: Donde almacenamos el token de Gitlab.

* _GITHUB\_COM\_TOKEN_: Donde almacenamos el token de Github.

* _RENOVATE\_EXTRA\_FLAGS_: Donde almacenamos la configuración de la aplicación.

![renovate-vars](https://storage.googleapis.com/tangelov-data/images/0042-01.png)

En la última variable tenemos el siguiente contenido: ```--autodiscover=true --autodiscover-filter=tangelov-functions/*```. Esta configuración hace que Renovate busque todos los repositorios disponibles dentro del grupo _tangelov-functions_ de forma automática. Pese a que la documentación no es muy clara, podemos ver todas las opciones disponibles con el comando ```docker run -ti renovate/renovate --help```

![renovate-config](https://storage.googleapis.com/tangelov-data/images/0042-02.png)

Por último tendremos que crear un _Schedule_ en Gitlab, donde configuramos la periodicidad de los análisis. Para hacerlo, vamos a CI/CD, Schedules_ y rellenamos los valores periodicidad y que apunte a la rama master/main.

Si ahora lo ejecutamos a mano, podemos ver los resultados del análisis:

![renovate-schedules](https://storage.googleapis.com/tangelov-data/images/0042-03.png)

```
INFO: Autodiscovered repositories
       "length": 3,
       "repositories": [
         "tangelov-functions/gcp-billing-notifications",
         "tangelov-functions/messages-to-matrix",
         "tangelov-functions/checking-drive-backups"
       ]
 INFO: Repository started (repository=tangelov-functions/gcp-billing-notifications)
       "renovateVersion": "25.21.11"
 INFO: Repository is disabled - skipping (repository=tangelov-functions/gcp-billing-notifications)
 INFO: Repository finished (repository=tangelov-functions/gcp-billing-notifications)
       "durationMs": 1626
 INFO: Repository started (repository=tangelov-functions/messages-to-matrix)
       "renovateVersion": "25.21.11"
 INFO: Repository is disabled - skipping (repository=tangelov-functions/messages-to-matrix)
 INFO: Repository finished (repository=tangelov-functions/messages-to-matrix)
       "durationMs": 1289
 INFO: Repository started (repository=tangelov-functions/checking-drive-backups)
       "renovateVersion": "25.21.11"
 INFO: Repository is disabled - skipping (repository=tangelov-functions/checking-drive-backups)
 INFO: Repository finished (repository=tangelov-functions/checking-drive-backups)
```

Como podemos ver, Renovate ha detectado los repositorios automáticamente, aunque indica que están deshabilitados. Esto es debido a que no hemos configurado en los repositorios destino qué se debe buscar y analizar.

> En principio, en Github crea un Pull Request para configurar automáticamente en los repositorios detectados Renovate, pero a mi en Gitlab no me ha funcionado.

#### Integrando Renovate con nuestros repositorios
Para finalizar, tenemos que integrar Renovate en los repositorios de cada una de las funciones. Tan sólo tenemos que crear un fichero de nombre _renovate.json_ en la raíz de cada uno de ellos con el siguiente contenido:

```json
{
    "extends": [
      "config:base"
    ],
    "prConcurrentLimit": 0,
    "rebaseWhen": "never",
    "masterIssue": true,
    "pip_requirements": {
      "fileMatch": ["requirements.txt"]
    }
}
```

Esta fichero le indica a Renovate no hacer un _rebase_ nunca y buscar las dependencias de Python en el fichero _requirements.txt_. Es una configuración muy básica, por lo que me remito a la documentación oficial puesto que se puede hacer que los MR se automergeen tras un testing, etc.

Tras crear los ficheros, debemos volver a ejecutar el schedule del proyecto del runner y éste creará automáticamente una serie de Merge Requests con las dependencias que necesitan alguna actualización y un _Dashboard_ dentro de una _issue_ en Gitlab, donde podemos gestionarlos.

![renovate-example](https://storage.googleapis.com/tangelov-data/images/0042-04.png)

De esta forma podemos ir actualizando las dependencias y tener un registro de los cambios realizados:

![renovate-dashboard](https://storage.googleapis.com/tangelov-data/images/0042-05.png)


### Conclusiones
Renovate me ha demostrado ser de mucha ayuda a la hora de reducir el trabajo _no productivo_ en el mantenimiento de mis aplicaciones. Por ejemplo, cuando en el futuro añada tests a las funciones, podré actualizar las dependencias de forma automática, mejorando aun más todo el proceso.

Y con esto el post ha terminado, espero que os haya gustado y sirva a alguien más para gestionar una de las partes más tediosas de nuestro día a día.

 
## Documentación

* [The Full Story of the Stunning RSA Hack Can Finally Be Told (ENG)](https://www.wired.com/story/the-full-story-of-the-stunning-rsa-hack-can-finally-be-told/)

* [Definition of Supply Chain Attack in Wikipedia (ENG)](https://en.wikipedia.org/wiki/Supply_chain_attack)

* [Modelo de responsabilidad compartida en Amazon Web Services](https://aws.amazon.com/es/compliance/shared-responsibility-model/)

* [Página oficial de Renovate Bot (ENG)](https://www.mend.io/renovate/)

* [Github de Renovate Bot (ENG)](https://github.com/renovatebot/renovate)

* [Renovate-runner para Gitlab.org (ENG)](https://gitlab.com/renovate-bot/renovate-runner/)

* [Configuración de Renovate en los repositorios _cliente_ (ENG)](https://docs.renovatebot.com/configuration-options/)

* [Ejemplo de Renovate para Python (ENG)](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/renovate.json)

Revisado a 01-05-2023

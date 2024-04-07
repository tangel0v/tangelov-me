---
title: "Atlantis: Terraformando a través de GitOps"
slug: atlantis-i
authors:
  - tangelov
date: 2022-10-16T20:00:00+02:00
tags:  ["devops", "terraform", "gitops"]
categories: ["cloud"]
draft: false
---

Gestionar infraestructura es una de las cosas que más ha cambiado en los últimos años. Aún recuerdo mis primeros años en el sector, pasando mi jornada laboral creando scripts en Bash o Powershell y manteniendo o actualizando servidores casi constantemente.

Hoy en día todo ha cambiado mucho. Gracias al uso de las nubes, públicas y privadas, y a la proliferación de herramientas para gestionar infraestructura como código (IaC), nuestro trabajo se ha transformado. Ahora somos más parecidos a desarrolladores (con conocimientos de sistemas) y nos dedicamos a escribir código, realizar tests, diversas automatizaciones y a crear procesos para garantizar que nuestros cambios no vayan a romper nada.

La IaC nos ha permitido dar solución a muchos problemas, pero también ha generado otros. Trabajar en equipo puede ser desafiante y nuestro código debe ser integrado y aplicado con orden y control. Aunque no es la primera vez que trato este tema en el blog, hoy os voy a presentar una herramienta que puede ayudaros a lograr este propósito: __Atlantis__. 
<!--more-->


## ¿En qué consiste GitOps?
Atlantis es fundamentalmente, una herramienta Open Source que nos permite gestionar infraestructura a través de Terraform y una metodología de trabajo llamada __GitOps__.

Llamamos _GitOps_ a una serie de prácticas que nos permiten gestionar nuestra infraestructura y su configuración utilizando Git. De esta forma, nuestros repositorios de código se convierten en la única fuente de verdad y contienen el estado deseado de la infra.

GitOps traslada los mecanismos utilizados para gestionar el código de las aplicaciones a la infraestructura. De esta forma, podemos modificar nuestra infraestructura en función de los cambios y acciones realizados en nuestro repositorio. Por ejemplo, podríamos abrir un _Pull Request_ y que una herramienta nos estimara que recursos van a ser añadidos, que modificaciones va a sufrir nuestra infra y el coste que va a tener en nuestra factura.

Usar GitOps tiene algunos puntos fuertes:
* Proporciona una gran trazabilidad en los cambios. Los flujos de trabajo definidos permiten ver que cambios se han ido haciendo sobre la infraestructura y quién los ha realizado o autorizado.
* Permite la revisión del código de la infraestructura a través de pares, ayudando a detectar errores entre miembros del equipo antes de que éstos sean aplicados.
* Proporciona un marco / lenguaje común entre desarrolladores de aplicaciones y _desarrolladores de infraestructura_ que puede ayudar a reducir la fricción entre Dev y Ops.

Sin embargo, nada es perfecto y personalmente creo que también aporta algunos pequeños inconvenientes:
* La revisión entre pares puede relajar ciertos estándares de calidad y hacer que los desarrolladores se fíen más en las revisiones que en el testing.
* Exige aprender ciertas prácticas de programación que no todo el mundo tiene y que puede conllevar una mayor dificultad a la hora de introducir nuevos miembros en el equipo.


## Atlantis
Atlantis es una aplicación ligera, desarrollada en Go y con una interfaz web que nos permite realizar GitOps sobre nuestro código de Terraform. Para utilizarlo tenemos que desplegarlo nosotros en un servidor o en algún orquestador de contenedores puesto que no ofrece ninguna solución en SaaS. Resumiéndolo mucho, Atlantis ejecuta ```terraform plan``` y ```terraform apply``` de forma remota y nos devuelve el resultado a través de un comentario en el repositorio al que lo enlacemos.

Este sería, de forma simplificada, uno de los workflows que podemos realizar con Atlantis:

![workflow-example](https://storage.googleapis.com/tangelov-data/images/0048-00.png)

1. Un desarrollador realiza una serie de cambios en su código y abre un Pull Request / Merge Request sobre una rama.
2. Atlantis recibe la notificación de que una nueva rama ha sido abierta y utiliza ese código para ejecutar _terraform plan_
3. El MR recibe la salida del plan generado por Atlantis y lo adjunta como comentario en el mismo.
4. Si el desarrollador decide que el MR está listo para ser mergeado, puede comentar _atlantis apply_ para que Atlantis aplique los cambios. Dependiendo de lo que definamos en Atlantis, este paso puede ser totalmente automático.

### Configuración
Aunque la documentación de Atlantis es buena, creo que puede llegar a ser un poco liosa. Voy a intentar clarificar todo el proceso y a hacer un pequeño resumen a mi manera. 

Para comenzar a utilizar la herramienta, necesitamos configurar dos puntos: el _servidor_ y el _cliente_.

El __servidor__ es el lugar donde vamos a ejecutar Atlantis. Puede ser una máquina virtual o un contenedor, dependiendo de nuestras preferencias. Aquí vamos a necesitar configurar cuatro aspectos fundamentales de la aplicación:
* Un proveedor de Git válido: Atlantis no arranca si no configuramos uno de los cuatro proveedores de Git que soporta: Github, Gitlab, Azure DevOps y Bitbucket. Cada uno tiene sus diferencias y su propia documentación.
* Una ACL que valida que repositorios van a utilizar Atlantis. La aplicación no arrancará si no configuramos previamente una lista de repositorios a los que permitimos conectarse a la misma.
* Aspectos varios de la aplicación que modifican sus valores por defecto: el dominio a utilizar, el puerto donde el servicio escucha por defecto, etc.
* Permisos para aplicar cambios en Terraform. Como Atlantis descarga los binarios de Terraform para poder generar los planes, necesita los mismos permisos que Terraform. Si esto os puede parecer un posible problema de seguridad, en futuros posts vamos a ver cómo mitigarlo y controlarlo.

El __cliente__ es cualquier repositorio de Git que vaya a integrarse con el servidor del punto anterior. Requiere dos configuraciones:
* Un fichero de CI/CD: Atlantis utiliza un fichero de nombre _atlantis.yaml_ para definir el comportamiento de los workflows que pueden ejecutarse sobre este código.
* Un webhook: Atlantis necesita recibir los cambios realizados en el código a través de un webhook para que pueda interactuar con nuestro proveedor de Git y sus Pull/Merge Request.

Tras este pequeño resumen, ahora voy a mostrar paso a paso cómo integrar un repositorio de Gitlab dentro de Atlantis.

#### Creación del usuario robot
Nuestro primer paso es [crear un nuevo usuario](https://docs.gitlab.com/ee/user/profile/account/create_accounts.html#create-users-on-sign-in-page) en Gitlab para Atlantis. Mi recomendación es crear uno dedicado para el bot para evitar que los comentarios dejados por Atlantis salgan con otro nombre y complique la trazabilidad del sistema.

Una vez creado el usuario, necesitamos un token que permita a Atlantis conectarse al proveedor de Gitlab a través de la API. Para ello nos vamos a _Preferences_ y de ahí a _Access Tokens_. Una vez allí, creamos un token con permisos de _api_ y lo guardamos para usarlo posteriormente:

![gitlab-api-token](https://storage.googleapis.com/tangelov-data/images/0048-01.png)

Aunque Atlantis ya podría conectarse a Gitlab, sin permisos sobre nuestros repositorios sería algo inútil. Nuestro siguiente paso es darle acceso a los mismos, usando alguno de los roles que Gitlab tiene predefinidos. Podemos elegir entre _Maintainer_ o _Developer_:

![gitlab-permissions](https://storage.googleapis.com/tangelov-data/images/0048-02.png)

#### Configurando el servicio de Atlantis
Atlantis proporciona binarios y una [imagen oficial](https://github.com/runatlantis/atlantis/pkgs/container/atlantis) de Docker que podemos utilizar para ejecutarlo.

Tras preparar nuestro usuario robot en Gitlab, el siguiente paso es configurar Atlantis y ponerlo en funcionamiento. Cambiar el comportamiento del servicio es sencillo y podemos hacerlo de diferentes formas: pasándole parámetros al arrancar, con variables de entorno o con ficheros de configuración. Podemos ver [aquí](https://www.runatlantis.io/docs/server-configuration.html) todas las opciones disponibles.

Para este caso concreto, vamos a crear dos ficheros:
* En el primero, vamos a configurar la integración con nuestro proveedor de Git y algunas características extra de seguridad.
* En el segundo, vamos a definir los comportamientos que permitimos en los pipelines de nuestros repositorios _clientes_:

Nuestro primer fichero, llamado _config.yaml_, contiene los siguientes datos:

```yaml
port: "8080"
gitlab-user: "< usuario-gitlab >"
gitlab-token: "< token-usuario-gitlab >"
gitlab-webhook-secret: "< cadena-de-texto-para-validar-los-webhooks >"
repo-allowlist: "gitlab.com/tangelov/*"
atlantis-url: "http://atlantis.tangelov.me"
web-basic-auth: "true"
web-username: "administrator"
web-password: "< contraseña-de-administrador >"
```

La configuración realizada es la siguiente
* Cambiamos el puerto en el que escucha el servicio. Por defecto, Atlantis escucha en el puerto 4141 pero yo prefiero que lo haga en el puerto 8080 por estandarización.
* Definimos el usuario de Gitlab y el token necesarios para que Atlantis pueda autenticarse contra la API de Gitlab.
* Definimos un secreto a modo de contraseña que debemos usar para validar las llamadas al webhook de Atlantis. Debe ser una cadena de texto aleatoria.
* Definimos la URL de nuestro servicio, siendo utilizada para generar los links a cada uno de los planes creados por Terraform.
* Añadimos una lista con los repositorios a los que Atlantis puede acceder. En este caso le he dado acceso a todos mis repositorios en Gitlab.
* Habilitamos la autenticación de la consola web del servicio para evitar que nadie que no conozca su contraseña pueda ver los planes generados por Atlantis e interactuar con ellos.

Ahora creamos un segundo fichero, cuya estructura podemos consultar [aquí](https://www.runatlantis.io/docs/server-side-repo-config.html). Puede tener el nombre que queramos pero yo lo he llamado _repos.yaml_:

```yaml
repos:
 - id: /.*/
   allowed_overrides: [workflow, apply_requirements, delete_source_branch_on_merge]
   allow_custom_workflows: true
```

En este caso, le indicamos al servicio que cualquier repositorio cliente pueda configurar su propio workflow (sea personalizado o no, hablaremos más adelante de esto), definir sus propios requisitos para hacer un _apply_ o borrar la rama creada cuando ésta sea integrada.

Ahora podríamos ejecutar Atlantis con los siguientes parámetros:

```bash
podman run \
  -v $(pwd)/config.yaml:/usr/local/bin/config.yaml \
  -v $(pwd)/repo.yaml:/usr/local/bin/repo.yaml \
  -p 8080:8080 \
  ghcr.io/runatlantis/atlantis:v0.20.1 \
  server --config=/usr/local/bin/config.yaml --repo-config=/usr/local/bin/repo.yaml
```

Ya deberíamos poder acceder al servicio utilizando http://localhost:8080 tras introducir un usuario y una contraseña:

![atlantis-service](https://storage.googleapis.com/tangelov-data/images/0048-03.png)


#### Integrándolo todo
En este punto ya hemos configurado el servicio y lo hemos desplegado en un servidor. Nuestro siguiente paso es conectar nuestros repositorios a Atlantis.

Para hacerlo necesitamos crear un nuevo webhook. Dentro de Gitlab accedemos a nuestro repositorio, le damos a _Settings_ y seleccionamos _Webhooks_:

![gitlab-webhook](https://storage.googleapis.com/tangelov-data/images/0048-04.png)

Una vez allí, creamos un nuevo webhook con los siguientes datos:
* _URL_: es el dominio completo de nuestra instancia de Atlantis terminada en _/events_, que es donde Gitlab va a mandar los eventos que generemos.
* _Secret Token_: debe tener el mismo contenido que la variable _gitlab-webhook-secret_ en la configuración de Atlantis. Se utiliza para validar la autenticidad de los eventos generados por Gitlab.
* _Trigger_: Aquí seleccionamos los eventos que queremos que llamen al webhook. En este caso vamos a seleccionar dos _Push Events_ (al crear un nuevo Merge Request) y _Comments_ (para poder darle órdenes a Atlantis al comentar en Gitlab).

Por último, debemos crear un fichero llamado _atlantis.yaml_ en la raíz del repositorio, donde le indicaremos a Atlantis los pasos que debe seguir con el código de este repositorio. 

```yaml
version: 3
automerge: false
delete_source_branch_on_merge: true
parallel_plan: false
parallel_apply: false
projects:
- name: dummy
  dir: .
  terraform_version: v1.2.8
  delete_source_branch_on_merge: true
  apply_requirements: [mergeable, approved]
  workflow: standard
workflows:
  standard:
    plan:
      steps:
      - run: mkdir -p apply-tfvars && mkdir -p init-tfvars
      - run: echo "${PRD_INIT_VARS}" > init-tfvars/dev.tfvars
      - run: echo "${PRD_APPLY_VARS}" > apply-tfvars/dev.tfvars
      - init:
          extra_args: ["-backend-config", "./init-tfvars/dev.tfvars"]
      - plan:
          extra_args: ["-var-file", "./apply-tfvars/dev.tfvars"]
allowed_regexp_prefixes:
- feature/
- fix/
```

Atlantis nos permite aplicar una gran cantidad de [configuraciones](https://www.runatlantis.io/docs/repo-level-atlantis-yaml.html#do-i-need-an-atlantis-yaml-file) diferentes, así que voy a explicar un poco lo que he definido para este ejemplo:
* Primero pongo ciertas limitaciones a Atlantis: no permito que los MR sean mergeados automáticamente ni que se hagan ejecuciones paralelas. También definimos una versión por defecto de Terraform para este proyecto.
* Después creo un proyecto, llamado _dummy_, e indico dónde está su código, que requisitos necesita para mergearse a la rama principal y el workflow que va a utilizar (en este caso, _standard_).
* Por último definimos los distintos workflows que podemos usar para este repositorio. Este es bastante sencillo y tan sólo coge el contenido de las variables de entorno PRD\_INIT\_VARS y PRD\_APPLY\_VARS, los convierte en ficheros y ejecuta ```terraform init``` y ```terraform plan``` con algunos parámetros extra.
* También limitamos que solo se ejecute en ramas cuyo nombre empiece por _feature/_ o _fix_.

> Debido a que configuramos Terraform utilizando dos variables de entorno extra, éstas deberán ser definidas en el servidor o contenedor donde Atlantis esté siendo ejecutado. En caso de no hacerlo, Atlantis será incapaz de ejecutar Terraform correctamente.

Si ahora realizamos un Merge Request, veremos cómo Atlantis nos muestra los cambios en Gitlab:

![gitlab-atlantis](https://storage.googleapis.com/tangelov-data/images/0048-05.png)

Si ahora dejamos un comentario con ```atlantis apply -p dummy```, dicho plan sería aplicado automáticamente.


### Posibilidades
Atlantis abre un gran abanico de posibilidades gracias a dos funcionalidades que están integradas por defecto:

* El soporte nativo de Unit Testing. Atlantis integra una de las herramientas más utilizadas en este campo, Open Policy Agent. Atlantis permite ejecutar la última versión estable de Conftest y realizar tests sobre nuestro plan. Así evitamos aplicar configuraciones no deseadas sobre nuestra infraestructura y garantizar que no rompemos nada que no deberíamos. Hace tiempo escribí un artículo al respecto que puede ser consultado [aquí](https://tangelov.me/posts/opa.html).

* Otro puntazo es la posibilidad de añadir workflows personalizados, que modifican el comportamiento de Terraform por defecto, así como nuevos binarios o scripts, que pueden ser ejecutados dentro de Atlantis sin problemas. De esta forma podemos adaptar las funcionalidades de la herramienta a las necesidades de cualquier equipo y ejecutar otras herramientas como Terragrunt o Terraform CDK.

Por último me gustaría hablar sobre el tamaño del contenedor oficial. Es ENORME (para lo que debería ser), es un contenedor de 725 MB porque a la hora de construirlo se descargan todas las versiones estables de Terraform desde la 0.11 hasta la más actual. Si alguien necesita crear un contenedor personalizado (ya sea para añadir nuevas herramientas o scripts), recomiendo adelgazar el contenedor y seleccionar solo las que vaya a utilizar.

De todo esto hablaremos en un futuro post que estoy preparando, con un workflow complejo de principio a fin y que muestra las posibilidades de Atlantis. Esto solo es un pequeño aperitivo.

### Conclusiones
En general, es una herramienta que me ha gustado. Es versátil, potente y se adapta tanto a mis necesidades actuales como a las que creo que tendré en un futuro. Creo que cualquier organización que utilice Terraform y tenga un nivel de madurez mínimo podría exprimir todo su jugo. Me ha encantado por ejemplo que Gitlab detecte que Atlantis está gestionando los pipelines y nos lo muestra en el propio repositorio.

Sin embargo, no es una aplicación perfecta y tiene ciertas lagunas, especialmente en temas de seguridad.

Gran parte de las funcionalidades de Atlantis se solapan con las versiones corporativas de Terraform (Cloud o Enterprise). Imagino que está relacionado con que el principal desarrollador de Atlantis fuese contratado por Hashicorp hace años. Atlantis tampoco tiene soporte para usuarios o grupos y no encapsula cada proyecto, son simplemente carpetas dentro del sistema de ficheros del servidor donde se ejecute. Esto hace que nuestra instancia de Atlantis tenga acceso a todas las credenciales usadas por todos los repositorios, por lo que me imagino que con un poco de ingeniería social, puedes hacer _maldades_. 

La única forma de solventar esto es mediante el uso de instalaciones privadas de Atlantis para cada proyecto o integrándolo con Terraform Cloud (que soluciona muchos de los problemas aquí comentados). Para el ejemplo de este post, tenemos que definir las variables de entorno directamente en Atlantis. Si tenemos múltiples proyectos y entornos por proyecto, no vamos a poder escalarlo y va a ser necesario gestionar los permisos de Terraform de forma diferente. En un próximo post hablaré específicamente de este tema.

Por último me gustaría comentar que tengo dudas sobre su utilidad en proyectos muy grandes y con muchas carpetas anidadas. Un plan completo podría llegar a crear tantos comentarios que podrían generar más ruido que información si no se gestiona adecuadamente.

Pese a todo, la herramienta me ha encantado y no creo que tenga más problemas que la versión Open Source de Terraform. No puedo terminar este post sin agradecer a sus desarrolladores el esfuerzo y el mimo puesto en ella, en su documentación y darles las gracias.

Con esto termina mi primer post sobre Atlantis y nos vemos en el siguiente.

¡Un saludo!


## Documentación

* [Página oficial de Atlantis (ENG)](https://www.runatlantis.io/)

* [¿Qué es GitOps?](https://www.redhat.com/es/topics/devops/what-is-gitops)

* [Github oficial de Atlantis (ENG)](https://github.com/runatlantis/atlantis)

* [Configuración del servidor de Atlantis (ENG)](https://www.runatlantis.io/docs/server-configuration.html)

* [Random String and Numbers generator (ENG)](https://www.browserling.com/tools/random-string)

* [Atlantis repository configuration (ENG)](https://www.runatlantis.io/docs/repo-level-atlantis-yaml.html#do-i-need-an-atlantis-yaml-file)

* [Conftest Policy checking (ENG)](https://www.runatlantis.io/docs/policy-checking.html)

* [Custom Workflows in Atlantis (ENG)](https://www.runatlantis.io/docs/custom-workflows.html)

* [Security in Atlantis (ENG)](https://www.runatlantis.io/docs/security.html)

Revisado a 01-05-2023

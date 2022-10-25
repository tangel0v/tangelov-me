---
title: "Clound Run: orquestando contenedores sin Kubernetes"
slug: cloud-run
authors:
  - tangelov
date: 2022-10-25T05:00:00+02:00
tags:  ["devops", "terraform"]
categories: ["cloud"]
draft: false
---

Kubernetes es el orquestador de contenedores más utilizado del mundo. Gracias a su rápido ciclo de desarrollo, no ha parado de incorporar nuevas funcionalidades, que han cubierto nuevos casos de uso y le han permitido alcanzar un crecimiento casi exponencial.

Este ciclo de desarrollo también tiene sus _problemas_. Cada vez es más difícil y complejo mantener un cluster de Kubernetes y esto ha hecho que aparezcan orquestadores alternativos para cubrir los casos de uso más habituales.

Tenemos múltiples opciones. Si queremos ejecutar contenedores en nuestros servidores, podemos optar por _Docker Swarm_ (de Docker Inc.), o _Nomad_ (de Hashicorp.) Si somos usuarios de algún proveedor de nube pública, tenemos otras opciones nativas. El primer orquestador en aparecer fue _Google App Engine Flexible_, pero lo que se considera "standard" para este tipo de servicios fue definido por Amazon en _AWS Fargate_.

Todos estos orquestadores de nube pública tienen algo en común. Buscan ofrecer una plataforma que permita al desarrollador centrarse lo máximo posible en desarrollar su aplicación y reducir al máximo los costes operacionales y el mantenimiento de la infraestructura. Son servicios privativos, muy integrados con otros servicios de la plataforma.

Si en AWS tenemos __Fargate__ y en Microsoft Azure tenemos __Azure Container Apps__, la solución de Google Cloud es __Cloud Run__. En este post vamos a ver las características de Cloud Run y cómo adaptar una aplicación para que ésta pueda ejecutarse en dicha plataforma.

<!--more-->


## Cloud Run
Cloud Run es el principal orquestador de contenedores no-basado en Kubernetes de Google Clou. Desarrollado sobre Knative, tan sólo necesita una imagen, unos parámetros de configuración y él se encargará de mantener nuestra aplicación en ejecución.

Estas son sus características principales:

* Servicio totalmente gestionado con redundancia regional y autoescalado, sin gestionar ningún tipo de infraestructura.

* Pago por uso. Por defecto, sólo se nos cobra cuando nuestro código está en ejecución.

* Soporte nativo para Node.js, Go, Java, Kotlin, Scala, Python, .NET, aunque podemos usar cualquier otro lenguaje a través de contenedores.

* Soporte para los protocolos HTTP/1.*, HTTP/2, WebSockets y gRPC.

* CI/CD nativo gracias al uso de Cloud Build (con soporte a GitHub, BitBucket y Cloud Source Repositories).

* Integración nativa con algunos servicios de GCP como Secret Manager, Cloud Logging, Cloud Monitoring, o a través de _Serverless Connectors_ (Cloud SQL, Cloud Memorystore, Cloud Filestore, etc.).

Al basarse en Knative, Cloud Run tiene sus mismas características y es un servicio ideal para ejecutar aplicaciones _serverless_ y/o que respondan ante eventos (_Event Driven Applications_).

La aplicación perfecta para Cloud Run es una aplicación sin estado y que responda ante eventos, ya sea una petición HTTP o un mensaje dejado en una cola de mensajería.

### Diferencias con la competencia
Cloud Run es comparado con otros servicios similares como AWS Fargate o Azure Container Apps, pero tiene algunas diferencias (y similitudes con estos servicios) que debemos conocer antes de empezar a utilizarlo.

Para empezar, Cloud Run puede ejecutarse en dos generaciones distintas de runtime.

La primera generación cuenta con bastantes limitaciones. No proporciona [compatibilidad total](https://cloud.google.com/run/docs/troubleshooting#sandbox) en llamadas al sistema operativo, ni tampoco permite usar sistemas de ficheros en red como NFS, SMB, etc. Todo ello puede impactar a nuestra aplicación y no funcionar correctamente.

La segunda generación solventa todos estos problemas y ofrece un mayor rendimiento a cambio de requerir más memoria. Podemos ver todas las diferencias [aquí](https://cloud.google.com/run/docs/about-execution-environments).

Otra diferencia importante es relativa al coste. Su tier gratuito es muy generoso y el servicio se puede "auto-apagar" para reducir el coste. Así sólo se nos cobra por los recursos utilizados cuando la aplicación se está ejecutando. Azure Container Apps tiene el mismo modelo de negocio, pero AWS Fargate nos obliga a tener al menos una copia en ejecución.

Por último, Cloud Run (y su competencia) no tiene persistencia. Cualquier fichero escrito en el contenedor se perderá si éste se reinicia. La diferencia entre la solución de Google y su competencia es que Cloud Run utiliza la memoria RAM como sistema de almacenamiento y si escribimos mucho en disco, podemos quedarnos sin memoria.

## Desplegando Atlantis sobre Cloud Run
Tras haber revisado la documentación, ya podemos probar el servicio. En este post, y enlazando directamente con el [anterior](https://tangelov.me/posts/atlantis-i.html), vamos a ver cómo desplegar Atlantis sobre Cloud Run.

Atlantis proporciona [guías](https://www.runatlantis.io/docs/deployment.html) para desplegar la aplicación en distintos _sabores_ de Kubernetes, así como Docker o Fargate, por lo que deberíamos poder desplegarla en Cloud Run con algunos pequeños ajustes a su arquitectura.

### Requisitos
Antes de comenzar despliegue alguno, debemos realizar una toma de requisitos previa. ¿Cómo funciona Atlantis? ¿Qué problemas nos podemos encontrar?

Atlantis funciona de la siguiente manera:

* Al recibir un evento, clona el código del repositorio y lo almacena en local.
* Después ejecutará una serie de acciones definidas por nosotros: descarga los binarios y proveedores necesarios para ejecutar Terraform y generará un plan. Mientras dicho plan no sea aplicado o descartado, Atlantis generará un bloqueo temporal.
* Por último, aplicará el plan almacenado en local si se cumplen los requisitos.

Como podemos ver, Atlantis necesita un lugar persistente donde almacenar sus datos. Guarda en local los repositorios clonados y numerosos ficheros relacionados con Terraform (proveedores, módulos y planes). También guarda en una base de datos dentro de un fichero los bloqueos que identifican a cada plan.

Esto choca de forma directa con las características de Cloud Run por lo que debemos modificar un poco la arquitectura para que Atlantis funciona correctamente. Tenemos tres opciones:

* La primera opción implica montar un bucket de Google Cloud Storage como si fuera un disco a través del uso de [_gcsfuse_](https://github.com/GoogleCloudPlatform/gcsfuse) y almacenar ahí los datos persistentes de la aplicación.

![gcsfuse-atlantis](https://storage.googleapis.com/tangelov-data/images/0049-00.png)

* La segunda opción bebe directamente del módulo de Terraform para desplegar Atlantis sobre Fargate. De esta forma, guardamos los datos en algún sistema de ficheros en red como _Cloud Filestore_ o los _Cloud Volumes_ de NetApp.

![filestore-atlantis](https://storage.googleapis.com/tangelov-data/images/0049-01.png)

* La última opción sería no adaptar nada y asumir las consecuencias. Cuando la aplicación se caiga o sea re-desplegada, deberemos volver a ejecutar los planes que no se hayan aplicado.

Cada escenario tiene distintas ventajas e inconvenientes, por lo que antes de tomar una decisión, realicé varias pruebas de concepto.

La prueba basada en Cloud Storage no funcionó. Aunque era un poco lento, el principal problema fue la falta de compatibilidad plena de gcsfuse con POSIX. Repositorios que fallaban al clonarse, problemas en la ejecución de los binarios almacenados en Cloud Storage, etc.

![atlantis-errors](https://storage.googleapis.com/tangelov-data/images/0049-02.png)

La segunda prueba funcionó a la perfección. Era un poco más compleja al tener que configurar un [VPC Serverless Connector](https://cloud.google.com/vpc/docs/configure-serverless-vpc-access) para acceder a los ficheros. Sin embargo, la tabla de precios de Cloud Firestore, que impide reservar menos de 1 TB de datos, la convertían en una solución inviable al añadir 200 dólares extra al precio total de la solución.

Al final, la tercera solución fue elegida por coste y complejidad. Implica asumir que si la instancia de Atlantis se para o es actualizada, deberemos re-ejecutar los planes que no se hayan aplicado, pero no es algo que vaya a impactar mucho en mis workflows.

> Otra solución que no he probado es el uso de un bucket de Cloud Storage como almacenamiento intermedio. El estado es descargado de un bucket durante el arranque y [actualizado al parar o reemplazar la instancia](https://cloud.google.com/blog/topics/developers-practitioners/graceful-shutdowns-cloud-run-deep-dive). 


### Código en Terraform
Previo a comenzar cualquier despliegue, no debemos olvidar la configuración de nuestro usuario robot en Gitlab, tal y cómo vimos en el post anterior.

Con los deberes hecho, podemos proceder a desplegar nuestros recursos y dependencias utilizando Terraform y Gitlab CI.

![atlantis-architecture](https://storage.googleapis.com/tangelov-data/images/0049-03.png)

1. Todo el código del proyecto se almacena en Gitlab. Cualquier modificación lanza un pipeline de CI/CD que puede o generar una nueva imagen de Atlantis y/o aplicar el código de Terraform del proyecto.

	Si queremos que se genere una nueva imagen, deberemos modificar alguno de los ficheros dentro de la carpeta _docker_ y mergear el código a la rama _main_.

2. El siguiente paso es desplegar la infraestructura para que el servicio pueda funcionar. Necesitamos:

	1. Un repositorio de Artifact Registry para almacenar nuestras imagenes Docker. Cloud Run no permite usar imagenes de DockerHub o Github  así que vamos a crear [nuestra propia imagen](https://gitlab.com/canarias2/atlantis/-/raw/main/docker/Dockerfile), que además pienso personalizar en el futuro.

	2. Dos secretos en Secret Manager: uno para la configuración del servicio y otro para la de los repositorios gestionados por Atlantis.

	3. Una cuenta de servicio de IAM con múltiples permisos que le permiten a Atlantis acceder al contenido de los secretos.

	4. Un servicio en Cloud Run.  

	Si intentamos desplegar todo de golpe, el servicio de Cloud Run dará un error al no existir ni una configuración válida para Atlantis ni una imagen dentro del repositorio de Artifact Registry.

3. El siguiente paso es __manual__. Deberemos crear una versión nueva dentro de cada secreto con la configuración de [nuestro servicio](https://gitlab.com/canarias2/atlantis/-/raw/main/docker/dummy_atlantis_config.yaml) y de los [repositorios](https://gitlab.com/canarias2/atlantis/-/raw/main/docker/dummy_repo_config.yaml). Para cualquier duda al respecto, recomiendo revisar el [post previo](https://tangelov.me/posts/atlantis-i.html) a éste.

	La configuración del Atlantis no está directamente integrada en Terraform (de momento) porque quiero pensar mejor cual es la mejor forma de hacerlo.

4. El cuarto paso es generar una imagen de Atlantis, ya sea con el pipeline o a mano.

5. Si ejecutamos nuestro pipeline una vez más y Cloud Run ya se desplegará sin errores.

6. Por último podemos crear un [dominio personalizado](https://cloud.google.com/run/docs/mapping-custom-domains) para Atlantis, pero dependiendo de cómo dicho dominio esté gestionado, podremos automatizarlo o no. Por ello este paso es totalmente __opcional__, pero también manual.

Llegados a este punto nuestra aplicación es plenamente funcional, sin necesitar llaves de cuentas de servicio puesto que todos los permisos son gestionados de forma nativa. El código completo de la solución está disponible [aquí](https://gitlab.com/canarias2/atlantis).


### Limitaciones
Me ha encantado enfrentarme a este reto. Ha sido un proceso con bastante ensayo y error al no conocer Cloud Run, pero me ha servido para comprobar la letra pequeña y sus limitaciones frente a una aplicación real.

Antes de nada me gustaría comentar que sé que estaba intentando desplegar una aplicación con estado en un servicio no diseñado para ello, pero esperaba poder salvar dicho obstáculo gracias a la combinación de múltiples servicios. De esto va la arquitectura en nube pública.

La primera limitación ha sido el espacio mínimo a reservar en Cloud Filestore: 1 TB de datos. En el módulo oficial para AWS Fargate, el estado de Atlantis es almacenado en un pequeño disco dentro de EFS, que añade un coste marginal al proyecto. 

En Google, la cosa es distinta. El tamaño mínimo obligatorio es tan grande que lo descarta como opción para muchos proyectos. Quizás es algún tipo de política interna porque he estado revisando todos los servicios del marketplace (NetApp, Elastifile, etc) referentes a sistemas de ficheros en red y comparten este problema.

La segunda limitación ha sido el modo de facturación de Cloud Run. Aunque por defecto se nos factura según la CPU y Memoria RAM utilizada al responder peticiones, este modo no funciona bien con aplicaciones que ejecuten procesos en segundo plano (como otros procesos, _goroutines_, etc). Al definir el modelo de facturación completo, no por peticiones, se nos obliga a utilizar instancias mayores a 512 MB de RAM.

```bash
# Este es el error que recibiremos si utilizamos el modelo por defecto de Cloud Run

Initializing the backend...
╷
│ Error: Failed to get existing workspaces: querying Cloud Storage failed: Get "https://storage.googleapis.com/storage/v1/b/bucket-secreto/o?alt=json&delimiter=%2F&pageToken=&prefix=dummy%2F&prettyPrint=false&projection=full&versions=false": impersonate: unable to generate access token: Post "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/sa-account@fake-project.iam.gserviceaccount.com:generateAccessToken": net/http: TLS handshake timeout
│ 
```


La última limitación ha sido la integración del sistema de secretos, Cloud Run y Atlantis. Al arrancar, Atlantis comprueba que la extensión de configuración del servicio termine en .yaml. 

Sin embargo, Secret Manager no deja utilizar puntos en los nombres de los secretos y Cloud Run no nos deja personalizar el nombre de los ficheros con el que se montan los secretos dentro del servicio.


Para solucionarlo, he necesitado añadir un paso en el [script de arranque](https://gitlab.com/canarias2/atlantis/-/raw/main/docker/docker-entrypoint.sh) del contenedor, que copia el contenido del secreto y genera el fichero en el formato esperado.

Por último, me gustaría añadir una pequeña tabla con el coste aproximado de ejecutar Atlantis al mes en cada uno de los servicios totalmente gestionados dentro de Google Cloud:

|  __Servicio__ | __Coste__ | __Observaciones__ |
|:-------------------:|:---:|:---:|
| Cloud Run | [44 $](https://cloud.google.com/products/calculator/#id=39d0d70c-3e5b-4899-8c43-867ceed5ca41) | El estado se pierde al reiniciar o reemplazar la instancia |
| Cloud Run + Filestore | [260 $](https://cloud.google.com/products/calculator/#id=b8992b9c-ac6e-417c-8f59-f100c67f0987) | El servicio requiere configurar un VPC Serverless Connector |
| Autopilot | [73 $](https://cloud.google.com/products/calculator/#id=0eb70f19-337a-4320-8d69-b64bf1cb6e26) | El coste del clúster puede ser compartido entre múltiples servicios |

Y nada, con esto terminamos. Espero que os haya gustado y ¡nos vemos en el siguiente post!


## Documentación
* [Cloud Run en GCP (ENG)](https://cloud.google.com/run/docs)

* [AWS Fargate (ENG)](https://aws.amazon.com/fargate/?nc1=h_ls)

* [Azure Container Apps (ENG)](https://azure.microsoft.com/en-us/products/container-apps/)

* [Página oficial de Knative (ENG)](https://knative.dev/docs/)

* [Knative sobre GCP (ENG)](https://cloud.google.com/knative)

* [Código del proyecto en Gitlab (ENG)](https://gitlab.com/canarias2/atlantis)


Revisado a 25-10-2022

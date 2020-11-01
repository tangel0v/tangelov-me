---
title: "Platform9: Kubernetes as a Service en nuestro CPD"
authors:
  - tangelov
date: 2020-05-31T10:00:00+02:00
tags:  ["kubernetes", "devops", "monitorizacion"]
categories: ["cloud"]
draft: false
---

Al comenzar este blog hace más de dos años, siempre tuve claro que me centraría en la nube en sí misma, así como en las metodologías y tecnologías que permiten su existencia.

La tecnología no ha parado de evolucionar en estos años: han aparecido constántemente nuevas ideas, que buscan solucionar los problemas ya existentes, pero que a su vez generan otros nuevos problemas.

El propio Kubernetes es un ejemplo perfecto: permite aprovechar mejor los recursos que disponemos y aporta una mayor resilencia y disponibilidad. Sin embargo, también genera mucha abstracción en sus elementos y hace que podamos perder capacidad operativa y visibilidad. Sin las herramientas adecuadas es mucho más fácil corregir un error en una máquina virtual que en una aplicación desplegada en varios microservicios.

Personalmente, siempre me he centrado en los principales proveedores de nube pública. Son mi foco a nivel profesional y permiten reducir la complejidad que supone usar estas nuevas tecnologías, acercándolas a los usuarios, clientes y administradores menos _techies_.

Pero... ¿Y si no queremos utilizar nube pública? ¿No existe alguna alternativa potente para gestionar nuestra nube pública?

<!--more-->

## Introducción

![platform9-logo](https://storage.googleapis.com/tangelov-data/images/0031-00.png)

Platform 9 es una compañía californiana, fundada en 2013, que nos ofrece exactamente eso: convertir cualquier potencia de computación que tengamos en un servicio de nube gestionado por ellos. Es un sistema relativamente flexible, pudiendo sus herramientas sobre máquinas físicas o virtuales, desplegadas tanto en nuestros CPDs (VMWare, KVM, Virtualbox, etc) como en la nube (Amazon Web Services o Microsoft Azure). De esta forma, nuestros servidores se convierten en un SaaS al que accederemos a través de una consola web.

A día de hoy ofrecen dos servicios principales:

* __PMO__ o _Platform9 Managed OpenStack_ que es Openstack gestionado por ellos.

* __PMK__ o _Platform9 Managed Kubernetes_ que es su Kubernetes operado. Este servicio es el que vamos a probar y utilizar hoy.


Según su documentación __PMK__ ofrece lo siguiente:

* La creación de forma simple y automatizada de clústers de Kubernetes sobre cualquier infraestructura. Su sistema posee integración nativa con AWS o GCP, aunque podemos instalarlo en cualquier máquina física o virtual.

* El acceso a un catálogo integrado de aplicaciones (MySQL, Kibana, etc) que podemos desplegar directamente en nuestros clústers. Dicho catálogo se gestiona mediante Helm y está disponible para las distintas opciones de pago de PMK.

* La monitorización y gestión de logs de forma automática gracias al uso de Prometheus, Grafana y Fluentd, en un servicio 24x7. Podemos ampliar la capacidad operativa del equipo de PF9 si les damos acceso por SSH (más información [aquí](https://docs.platform9.com/openstack/troubleshooting/enable-ars/))

* Una gestión más sencilla de las operaciones de nuestro clúster: actualizaciones, aplicación de parches de seguridad, etc. También aporta una gestión totalmente centralizada para el sistema de RBAC de Kubernetes y de la autenticación de los usuarios.

Para comenzar a utilizar la plataforma, tenemos que crearnos una cuenta en su página web. Para hacerlo, hacemos click [aquí](https://platform9.com/signup/)


![platform9-signup](https://storage.googleapis.com/tangelov-data/images/0031-01.png)

Platform9 tiene diferentes tiers con diferentes precios en función de las necesidades del cliente. En nuestro caso vamos, a utilizar su _tier gratuito_, puesto que cubre de sobra nuestras necesidades (soporta hasta 3 clústers de Kubernetes y 20 nodos operados por ellos) y no requiere introducir ningún número de cuenta.

Tras el registro, podemos acceder a la plataforma para encontrarnos una interfaz similar a ésta.

![platform9-dashboard](https://storage.googleapis.com/tangelov-data/images/0031-02.png)


## Desplando PMK sobre máquinas virtuales

Aunque podría empezar a comentar la consola web, primero vamos a desplegar un clúster para que éste llene de información la consola.

> Antes de nada, que quede claro: no he sido contactado por nadie de Platform9. Simplemente descubrí su servicio y quise probarlo para ver que tal funcionaba cuando anunciaron su plan gratuito. No es [la primera vez](https://tangelov.me/posts/pulumi.html) que lo hago.

Para crear el clúster con Platform9, he preparado algo de infraestructura previamente en un pequeño servidor que tengo en casa. Como se trata de una prueba de concepto he creado tres máquinas virtuales sobre Virtualbox con las siguientes especificaciones:

* Un nodo _maestro_ con un core de CPU, 2 GB de RAM y 20 GB de disco duro. Su IP es la 192.168.1.114.

* Dos nodos _worker_ con un core de CPU, 4 GB de RAM y 50 GB de disco duro. Sus IPs son respectivamente, la 192.168.1.115 y la 192.168.1.116.

Todas las máquinas están basadas en Ubuntu 16.04, no tienen restricciones de red para facilitar las pruebas y tienen un usuario común que utilizaremos por SSH para dar de alta los nodos del clúster. 

Aunque PMK soporta integración con la nube (y es el método recomendado para AWS y Azure), en éste caso vamos a utilizar lo que ellos llaman _BareOS_. BareOS es el nombre que PMK utiliza en cualquier clúster que esté desplegado fuera de la integración nativa con la nube: máquinas físicas o máquinas virtuales montadas sobre VMWare, KVM o cualquier otro proveedor de infraestructura.

Para comenzar el despliegue, podríamos utilizar la consola web o la CLI. En este caso, voy a instalar la CLI de Platform9 en el maestro y realizar todas las operaciones desde ahí aunque podríamos instalarla en cualquier PC. Nos pedirá la URL de nuestra cuenta de Platform9 y nuestro usuario (que es nuestro correo electrónico):

```bash
# Primero instalamos la CLI de PMK
bash <(curl -sL http://pf9.io/get_cli)

Validating and installing package dependencies
INFO: using exising virtual environment
Upgrading pip
Installing Platform9 CLI

# Nos pedirá una serie de valores que tenemos que introducir
# La Account URL es la URL de la interfaz web a la que nos logueamos para acceder a nuestro cluster.

Please provide your Platform9 Credentials
Platform9 Account URL: https://pmkft-$identificador.platform9.io
Username: $correo_electronico
Enter Region & Tenant Details (Freedom Plan requires RegionOne and service)
Region [RegionOne]: RegionOne
Tenant [service]: service

Successfully wrote CLI configuration
Successfully validated the Platform9 account details
```

Tras instalar y configurar la CLI, ya podemos dar de alta un clúster. Para ello nos conectamos a la máquina donde hayamos instalado la CLI y ejecutamos el siguiente comando:

```bash
# Tarda unos minutos en completarse (hasta 15 minutos)
pf9ctl cluster create --master-ip 192.168.1.114 \
  --allowWorkloadsOnMaster false \
  --user $usuario \
  --password $passwordmolon \
  cluster-home
```

Así creamos un clúster llamado _cluster-home_ con un único maestro ubicado en la IP 192.168.114. También deshabilitamos explícitamente la ejecución de workloads en él puesto que vamos a utilizar los nodos _worker_ para ello.

El proceso de instalación es simple y relativamente rápido. La CLI nos mostrará cierta información sobre el proceso y nos informará del tiempo restante:

```bash
Preparing the local node to be added to Platform9 Managed Kubernetes
Preparing nodes  [####################################]  100%  

Creating Cluster: cluster-home
Using nodepool id: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
Waiting for cluster create to complete, status = True
Cluster cluster-home created successfully
Cluster UUID: ZZZZZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZZZZZZZZZ
Attaching to cluster cluster-home

Discovering UUIDs for the cluster's master nodes
Master nodes:
YYYYYYYY-YYYY-YYYY-YYYY-YYYYYYYYYYYY
Attaching master nodes to the cluster
Waiting for cluster to become ready
Attaching to cluster
Successfully attached to cluster
Waiting for all masters to become active  [#####-------------------------------]   16%  00:12:31
```

> En este post, sólo voy a generar un maestro, pero si alguien quiere generar uno con múltiples maestros, es necesario profundizar más en la documentación puesto que se añaden nuevos requisitos como indicar la interfaz de red de los maestros, etc.

Tras esperar unos pocos minutos nuestro clúster ya estará activo. Aunque ya podríamos conectarnos a él, vamos a añadir primero los nodos _worker_ para añadir potencia de computación y poder desplegar alguna aplicación. La propia CLI de Platform9 nos permite preparar y añadir los nodos al clúster, fácilmente y de forma automatizada.

Platform9 utiliza Ansible para preparar los nodos por lo que necesitamos que la cuenta de usuario que utilizamos por SSH pueda realizar operaciones administrativas sin contraseña. Para ello ejecutamos _visudo_ en ambos nodos y añadimos la siguiente línea: ```$usuario     ALL=(ALL) NOPASSWD:ALL```

Volvemos a la máquina donde hemos instalado la CLI de Platform9 y ejecutamos el siguiente comando:

```bash
pf9ctl cluster prep-node \
  --user $usuario \
  --password $password \
  --ips 192.168.1.115 \
  --ips 192.168.1.116

Preparing nodes  [####################################]  100%          
Preparing the provided nodes to be added to Kubernetes cluster was successful
```

El proceso de preparación añadirá las dependencias necesarias para funcionar como nodos de un clúster de PMK e instalará los agentes para convertirlos en nodos gestionados. Una vez haya terminado la preparación, ya podemos asociarlos a un clúster:

```bash
pf9ctl cluster attach-node \
  --worker-ip 192.168.1.115 \
  --worker-ip 192.168.1.116 \
  cluster-home

Attaching to cluster cluster-home
Discovering UUIDs for the cluster's worker nodes
Worker Nodes:
XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
YYYYYYYY-YYYY-YYYY-YYYY-YYYYYYYYYYYY
Attaching worker nodes to the cluster
Waiting for cluster to become ready
Attaching to cluster
Successfully attached to cluster
Successfully attached nodes to a Kubernetes cluster cluster-home using this node
```

Y así ya tendríamos un clúster completo, desplegado e integrado con Platform9 :)


## La plataforma de Platform9
Tras haber conectado el clúster, vamos a acceder a la consola web para ver que posibilidades nos ofrece.

Lo primero que observamos es un tutorial que nos permite configurar el acceso a través del CLI de Kubernetes (a través de un usuario y contraseña o mediante un token) y habilitar el sistema de monitorización, que actualmente se encuentra en beta.

![platform9-finish-config](https://storage.googleapis.com/tangelov-data/images/0031-03.png)

Con pocos clicks podremos descargar un kubeconfig que nos servirá para acceder al clúster. La manera más sencilla es mover dicho fichero a la carpeta _.kube_ en nuestro _$HOME_ y ponerle de nombre _config_.

> No olvidemos que si ya tenemos otros kubeconfig, debemos guardarlas antes para no perderlas.


### Interfaz web
La interfaz web es clara y nos permite gestionar fácilmente algunos de los aspectos de nuestro clúster.

![platform9-web-ui](https://storage.googleapis.com/tangelov-data/images/0031-04.png)

La consola se divide en dos partes principales: En la parte superior tenemos una barra de estado donde podemos seleccionar diferentes regiones (en el tier gratuito sólo podemos tener uno) y distintos tenant (luego hablamos de ello).

En la parte izquierda tenemos una lista de paneles donde accedemos a la plataforma de gestión. Son los siguientes:

* __Infrastructure__: Aquí vemos los diferentes clústers asociados a nuestra cuenta de Platform9 y su estado. También podemos realizar algunas operaciones tales cómo añadir o quitar nodos (maestros o workers), actualizar el clúster, habilitar backups de _etcd_, habilitar el sistema de soporte avanzado o configurar proveedores de Cloud pública.

* __Pods, Deployments, ServiceS__: Nos permite gestionar a una lista de los pods, servicios y deployments que tenemos desplegados en nuesta cuenta y filtrar por clúster, namespace o simplemente hacer una búsqueda. También podemos crear o borrar objetos nuevos.

* __Storage Classes__: Nos permite añadir, listar o borrar los diferentes proveedores de almacenamiento que tenemos configurados en cada uno de los clústers de nuestra cuenta.

* __Namespaces__: Nos permite ver, crear o borrar namespaces en cualquiera de los clústers que tengamos.

* __Monitoring__: Nos muestra todas las alarmas e incidencias que Platform9 ha detectado en nuestros clústers en un determinado rango de tiempo. En el tier gratuito son 24 horas.

* __RBAC__: Nos permite gestionar toda la autorización de todos nuestros clústers de Kubernetes, tanto a nivel de clúster (_ClusterRoles_ y _ClusterRoleBindings_) como a nivel de namespace (_Roles_ y _RoleBindings_)

* __API Access__: Permite generar los kubeconfig necesarios para que los usuarios puedan conectarse e interactuar con el clúster. Podemos generar kubeconfig mediante usuario y contraseña o bien a través de tokens.

* __Tenants & Users__: Permite generar usuarios y _tenants_ (grupos) a los que podemos asignar diferentes permisos y completar así la autenticación de los usuarios de nuestros clústers.

La mayoría de paneles permiten gestionar elementos internos de los clústers como los pods o el RBAC, pero hay tres de ellos que son un aporte diferente y que vamos a tratar más en profundidad.

#### Infraestructure
El panel de infraestructura es el punto donde gestionar nuestros clústers y se divide en tres partes: clusters, nodes y cloud providers:

* En _clusters_ podemos gestionar cada uno de los clústers. Escalar maestros, workers o habilitar el sistema de monitorización. Si hemos habilitado el sistema de monotirización, también podemos acceder desde _clusters_ a un panel del Grafana que nos muestra el estado de nuestros clústers.

    ![platform9-links](https://storage.googleapis.com/tangelov-data/images/0031-05.png)

    Aquí podemos ver a modo de ejemplo, parte de la información que nos proporciona Grafana:

![platform9-monitoring](https://storage.googleapis.com/tangelov-data/images/0031-06.png)

* En _nodes_ podemos ver el estado y características de cada uno de los nodos. También podemos habilitar el sistema de soporte remoto avanzado.

    ![platform9-nodes](https://storage.googleapis.com/tangelov-data/images/0031-07.png)

* En cloud provider podemos configurar la integración de Platform9 con alguno de los dos proveedores soportados (AWS y Azure). Como podemos ver en la captura de pantalla, la integración se hace a nivel de API y debemos proporcionar los datos necesarios para que ésta funcione correctamente.

    ![platform9-cloud-provider](https://storage.googleapis.com/tangelov-data/images/0031-08.png)

#### Monitoring
En el panel de monitoring podemos ver las incidencias detectadas por Platform9 y solucionadas, junto con las alarmas que han ido detectando.

![platform9-monitoring](https://storage.googleapis.com/tangelov-data/images/0031-09.png)

#### Tenants & Users
El panel de Tenants y Users es donde configuramos la autenticación y autorización sobre la consola de Platform9.

Aunque actualmente no sea posible, en el futuro también gestionará las regiones. Cada región constituye una agrupación lógica de recursos que se asocian a una zona geográfica. Para desplegar alguna región extra, en estos momentos tenemos que contactar al soporte de Platform9 (no con el Free Tierde PMK)

También podemos crear tenants y usuarios. Un tenant es una agrupación lógica de usuarios dentro de una organización, en una o más regiones. Los tenants administran los recursos (clústers y cloud providers) que hayan sido creados por alguno de los administradores de dicho tenant.

En cada tenant podemos asociar una serie de usuarios y a éstos podemos asociarle dos tipos de roles: usuarios y administradores. Los usuarios no privilegiados no pueden crear políticas de RBAC y no tendrán acceso a los clústers por defecto, teniendo un administrador que crear las políticas necesarias para que puedan acceder.

![platform9-tenants-users](https://storage.googleapis.com/tangelov-data/images/0031-10.png)


### Aplicaciones y operaciones
Una vez que ya hemos hecho un tour por lo que ofrece la plataforma, voy a añadir algo más de chicha a la prueba: vamos a desplegar una aplicación y hacerle algunas perrerías al clúster. La idea es desplegar una aplicación y realizar algunas tareas en los nodos que impacten en la viabilidad del clúster para ver cómo se comporta el conjunto.

Vamos a desplegar un CMS muy conocido llamado _Ghost_ a través de [Helm](https://helm.sh/docs/intro/install/). Sin entrar en muchos detalles, vamos a generar un fichero de configuración con el siguiente contenido:

```yaml
ghostHost: ghost.miprueba.test
service:
  type: NodePort
  port: 80
  nodePorts:
    http: 30000
readinessProbe:
  enabled: false
mariadb:
  master:
    persistence:
      enabled: false
persistence:
  enabled: false
```

Tras instalar Helm, ya podemos instalar el aplicativo ejecutando los siguientes comandos:

```bash
# Añadimos el repositorio de Bitnami para instalar Ghost
helm repo add bitnami https://charts.bitnami.com/bitnami

# Creamos el namespace ghost para almacenar la aplicación
kubectl create namespace ghost

# Desplegamos la aplicación
helm install ghost bitnami/ghost -f myvalues.yaml --namespace ghost
```

Ahora podemos ver en _Pods, Deployments, ServiceS_ el estado de la aplicación y el nodo en el que se encuentra cada uno de sus pods:

![platform9-k8s-ghost](https://storage.googleapis.com/tangelov-data/images/0031-11.png)

Si editamos nuestro _/etc/hosts_ y añadimos el registro _ghost.miprueba.test_ a la IP del nodo donde está desplegado Ghost, podremos acceder a la aplicación a través del link http://ghost.miprueba.test:30000

![platform9-ghost](https://storage.googleapis.com/tangelov-data/images/0031-12.png)


Nuestro blog de Ghost ya está ejecutándose, pero ahora vamos a hacerle algunas perrerías al clúster para ver que tal funciona el sistema.

* Al apagar el nodo de forma controlada un nodo worker, éste sigue apareciendo como Healthy en el Dashboard (entiendo que no lo detecta como una incidencia). También deja de funcionar el Grafana, imagino que al estar en beta no se despliega en alta disponibilidad. Sin embargo si que recibimos un correo sobre que uno de los nodos ha dejado de funcionar.

* Al borrar del hipervisor un nodo worker ocurre lo mismo que en el caso anterior. Si el nodo es el que tiene los workloads de Ghost, la monitorización en desde su consola sigue en estado _Running_, pero si accedemos al _Dashboard_ de Kubernetes incluido, si vemos que está caído.

* Al apagar el nodo maestro, tampoco muestra la caída en la consola. La sensación que tengo es que identifica dichas incidencias como algo natural. He probado a apagar un nodo maestro y un nodo worker y luego tiene que consolidar de nuevo el clúster durante el proceso de arranque de los nodos.

* He probado a llenar los discos y el sistema lo detecta rápidamente, aunque he detectado algunas inconcruencias en las mediciones de CPU que pueden estar relacionadas con el hipervisor y la máquina física usada.


## Conclusiones
Es una pena que no haya habido ninguna actualización de seguridad durante el tiempo que he tenido los clústers levantados. Me hubiera encantado ver su sistema de actualización y mantenimiento de parches: leyendo su documentación parece su principal punto fuerte. Hay algunas cosas que me han gustado mucho:

* Su sistema para crear clústers nuevos, incluso multi-maestro o arquitecturas complejas es muy sencillo, tanto a través de la interfaz web como a través de la CLI. Acerca muchísimo la tecnología al usuario final y las versiones que ofrecen de Kubernetes están en la línea con el de los proveedores de Cloud pública (en estos momentos ofrecen en BareOS la 1.15.9).

* La consola web es limpia y se centra en algo que la mayoría de clientes gráficos no hace: la autenticación y la autorización en Kubernetes. Si lo juntamos al sistema de _tenants_ y _regiones_ podemos tener un sistema consistente y muy potente.

* Su modelo de apoyo al software libre y el código abierto me parece admirable puesto que devuelven mucho trabajo a la Comunidad.

* El modelo de _Pricing_ me ha parecido muy claro y las diferencias entre los diferentes tiers de negocio también (aunque es un poco caro).

Sin embargo, no he salido satisfecho con sus sitemas de monitorización y detección de problemas. No sé si es que yo no he entendido bien su funcionamiento o que éste no era el correcto debido a utilizar máquinas virtuales que compartían núcleos de CPU. A veces daba información contradictoria o errónea y siempre esperé que si un nodo desaparecía, ésto se reflejara en la consola web.

Y nada... este ha sido todo el análisis, espero que a alguien le sea de utilidad y muchas gracias por leerme. ¡Hasta la próxima!


## Documentación

* [Página principal de Platform9 (ENG)](https://platform9.com/)

* [Github de Platform9 (ENG)](https://github.com/platform9)

* Servicios gestionados por Platform9 (ENG): [Managed Kubernetes](https://platform9.com/managed-kubernetes/) y [Managed OpenStack](https://platform9.com/managed-openstack/)

* [¿Qué es BareOS? (ENG)](https://docs.platform9.com/kubernetes/bareos/what-is-bareos)

* [Tenants y regiones en Platform9 (ENG)](https://docs.platform9.com/kubernetes/tenant-user-administration/regions_tenants/)

* [Creación avanzada de clústers de PMK a través de la CLI (ENG)](https://docs.platform9.com/kubernetes/PMK-CLI/create/)

* [Preparación de nodos para añadir a un clúster de PMK a través de la CLI (ENG)](https://docs.platform9.com/kubernetes/PMK-CLI/prep-node/)

* [Añadiendo nodos a un clúster de PMK a través de la CLI (ENG)](https://docs.platform9.com/kubernetes/PMK-CLI/cluster/attach-node/)

* [Helm de Bitnami para instalar Ghost en Helm Hub (ENG)](https://hub.helm.sh/charts/bitnami/ghost)

* [Comparación entre las diferentes versiones de Platform9 (ENG)](https://platform9.com/pricing/comparison/)


Revisado a 30-05-2020

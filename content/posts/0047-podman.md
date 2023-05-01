---
title: "Contenedores sin docker: alternativas de futuro"
slug: containers-without-docker
authors:
  - tangelov
date: 2022-04-03T13:00:00+02:00
tags:  ["docker", "contenedores", "podman"]
categories: ["cloud"]
draft: false
---

El impacto generado por Docker en la comunidad a la hora de popularizar los contenedores como unidad de despliegue de aplicaciones es enorme. Desde el inicio, propuso una solución dual con ciertos servicios de pago (DockerHub) y otros de código abierto (como la CLI y el _daemon_) que la comunidad podía utilizar sin coste alguno.

Este formato basado en un SaaS y un producto de código abierto ha sido replicado con éxito por otras compañías como Redis o MongoDB con cierto éxito. Sin embargo la monetización del software libre nunca ha sido sencilla y en este post vamos a repasar los últimos movimientos ocurridos en Docker y a mostrar alternativas a su ecosistema.

<!--more-->

## La _"caída"_ de Docker
Por definición los contenedores son una forma de virtualización dentro de un sistema operativo donde múltiples clientes comparten el mismo núcleo. Antes de la aparición de Docker ya existían soluciones parecidas (como _chroot_), pero que no eran exactamente contenedores.

Su nacimiento se produce en Solaris para saltar de ahí al sistema del pingüino a través de soluciones como OpenVZ o LXC. Docker se ganó a la comunidad y se extendió muy rápidamente gracias a su sencillez de uso. Introdujo dos innovaciones de gran calado:
* Un SaaS donde almacenar y compartir imágenes de contenedores entre los miembros de la comunidad (_DockerHub_).
* Un sistema de plantillas que permitía crear y mantener contenedores de forma sencilla (_DockerFiles_).

Su éxito fue tal que rápidamente se convirtieron en partners de algunas de las mayores compañías de software del mundo. Mientras tanto, la comunidad fue creando nuevos productos que mejoraban aún más la experiencia de uso o creaban alternativas al ecosistema propuesto por Docker.

Esta relación con terceros fue vista con cierto recelo desde Docker. Según lo que he podido leer, intentaron evitar que sus imágenes pudieran ser ejecutadas en otros sistemas o que se pudieran usar [repositorios de imágenes de terceros](https://github.com/moby/moby/issues/1988). Por este motivo Red Hat llegó a tener un fork completo de Docker con soporte para _systemd_.

Mientras tanto Docker continuó intentando monetizar sus productos: creó una versión empresarial de su _demonio_ y un orquestador de contenedores llamado _Docker Swarm_. Sin embargo, no fueron los únicos en mover ficha y Google, que había estado trabajando internamente en su propio orquestador, les propuso a Docker colaborar. Tras muchas discrepancias entre los involucrados, Google acabó lanzó Kubernetes por su cuenta y el resto [_es historia_](https://www.networkcomputing.com/cloud-infrastructure/kubernetes-continues-eat-container-orchestration-market-lunch).

La tracción generada por Kubernetes acabó haciendo mella en la mitad corporativa de Docker y a finales de 2019 fue vendida a Mirantis. Desde entonces Mirantis ha buscado aumentar sus ingresos imponiendo restricciones de todo tipo en los productos más utilizados del portfolio de Docker: DockerHub y Docker Desktop. 

A día de hoy existen cuotas bastante estrictas en el número de imágenes que podemos descargar sin pagar de DockerHub y tampoco podemos utilizar Docker Desktop en entornos corporativos si no pasamos por caja.

Ante los cambios la comunidad ha ido migrando hacia otras alternativas:
* Docker ha dictado durante años la forma de ejecutar contenedores, pero a día de hoy existen otras alternativas plenas como _containerd_ o _CRI-O_.
* Aunque Kubernetes use Docker, éste nunca ha sido 100% compatible con el orquestador y utiliza una capa de compatibilidad llamada Dockershim. Esta capa y el soporte a Docker va a ser eliminado definitivamente de Kubernetes en la versión 1.23.
* Las restricciones de uso han hecho que los desarrolladores hayan ido migrando hacia otras herramientas como _Podman_, _Minikube_ o _Rancher Desktop_ dependiendo de sus propias necesidades.

> Mirantis ha confirmado que van a mantener Dockershim y a ofrecer soporte por su cuenta.


## Podman: un reemplazo one-to-one de Docker
Podman es una desarrollo comunitario, con un fuerte apoyo de Red Hat, que permite ejecutar contenedores y pods de forma sencilla. Aunque busca ser un reemplazo 1:1 de todas las funcionalidades de Docker, también tiene algunas funcionalidades extra:
* Permite la ejecución de contenedores con o sin acceso a root y de hacerlo con o sin un demonio (a diferencia de Docker).
* Soporta tanto el uso de Dockerfiles como la creación de contenedores de forma interactiva.
* Soporta la ejecución de contenedores basados en Docker y en cualquier formato de imagen compatible con la OCI (Open Containers Iniciative).
* Permite la ejecución también de pods (agrupaciones de contenedores), así como gestionar secretos o volúmenes. Esta funcionalidad está pensada para facilitar una transición hacia Kubernetes y por ello también soporta los típicos YAMLs usados por este orquestador.

Para los casos más sencillos la sustitución de Docker por Podman es tan sólo desinstalar el primero, instalar el segundo y crear un alias que ejecute _podman_ al usar el comando _docker_. Para el resto de la comunidad es para quien escribo este post.

> Esto no es del todo cierto porque Podman utiliza por defecto el formato OCI de imágenes en lugar del de Docker. Si queremos hacer _podman build_ para crear una imagen no debemos olvidar pasarle el formato correcto o nuestro contenedor podría no funcionar como esperabamos: ``` podman build . -t superimagen:latest --format docker```

### Instalación de Podman
Tras explicar un poco sus funcionalidades más básicas, vamos a instalar la herramienta.

Su instalación en __Linux__ es sencilla: mi recomendación es utilizar los [repositorios oficiales de la herramienta](https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/) o [el rol de la comunidad](https://github.com/alvistack/ansible-role-podman) para tener una versión más actualizada.

En sistemas no-Linux, Podman al igual que Docker, utiliza una máquina virtual para ejecutar los contenedores. En Windows puede utilizar el subsistema WSL (Windows Subsystem for Linux) de forma nativa. En cualquier caso, la máquina virtual debe inicializarse previamente con el comando ```podman machine init```.

Una vez tenemos Podman instalado ya podemos ejecutar nuestro primer contenedor. A modo de ejemplo voy a utilizar otra vez Traccar, un sistema de tracking de dispositivos a través de GPS y que ya hemos usado en este blog en el pasado:

```bash
# Primero creamos una carpeta en /tmp para almacenar los logs
mkdir /tmp/traccar-logs

# Después, simplemente ejecutamos el contenedor y lo "demonizamos"
podman run \
 -d --restart always \
 --name traccar \
 --hostname traccar \
 -p 80:8082 \
 -p 5000-5150:5000-5150 \
 -p 5000-5150:5000-5150/udp \
 -v /tmp/traccar-logs:/opt/traccar/logs:rw \
 traccar/traccar:4.13-debian
```

Este comando busca ser bastante completo y utilizar muchas de las funcionalidades típicas de Docker:
* Ejecuta un contenedor basado en la imagen _traccar/traccar:4.13-debian_ y lo _daemoniza_.
* Mapea diferentes puertos entre el contenedor y el host a través de diferentes protocolos (TCP o UDP).
* Monta un volumen en el contenedor que nos permite consultar los logs de la aplicación directamente desde el host.

Inmediatamente después de ejecutar el comando ya empezamos a ver algunas diferencias respecto a Docker. Dependiendo de la versión de Podman es posible que nos pregunte en que repositorio queremos buscar nuestra imagen. Esto ocurre debido a que Podman no asume que DockerHub sea su repositorio por defecto y no comprende los nombres cortos que referencian a éste.

```bash
? Please select an image: 
  ▸ registry.fedoraproject.org/traccar/traccar:4.13-debian
    registry.access.redhat.com/traccar/traccar:4.13-debian
    docker.io/traccar/traccar:4.13-debian
    quay.io/traccar/traccar:4.13-debian
```

Para que Podman asuma que cualquier nombre corto referencia a DockerHub debemos cambiar la línea _short-name-mode_ del fichero _/etc/containers/registries.conf_ de _enforcing_ a _permissive_.

Sin embargo si continuamos lo más probable es que recibamos el siguiente error:

```bash
Error: rootless port cannot expose privileged port 80, you can add 'net.ipv4.ip_unprivileged_port_start=80' to /etc/sysctl.conf (currently 1024), or choose a larger port number (>= 1024): listen tcp 0.0.0.0:80: bind: permission denied
```

Podman utiliza por defecto contenedores _rootless_, que no requieren permisos de administrador en el host y que no pueden abrir puertos privilegiados (1-1023) en él. Para solucionarlo tenemos dos opciones: o bien ejecutamos podman con _sudo_ (algo a evitar siempre que sea posible) o cambiamos el puerto 80 a otro que no sea privilegiado como el 8080.

```bash
# Primero paramos y borramos el contenedor anterior para evitar algún error
podman stop traccar && podman rm traccar

# Volvemos a ejecutar el contenedor en un puerto no privilegiado
podman run \
 -d --restart always \
 --name traccar \
 --hostname traccar \
 -p 8080:8082 \
 -p 5000-5150:5000-5150 \
 -p 5000-5150:5000-5150/udp \
 -v /tmp/traccar-logs:/opt/traccar/logs:rw \
 traccar/traccar:4.13-debian
```

Tras este último cambio, el comportamiento es el esperado y podemos acceder a Traccar a través de http://localhost:8080

![traccar-on-podman](https://storage.googleapis.com/tangelov-data/images/0047-00.png)


### Compatibilidad con Docker
Este post no pretende mostrar todas las funcionalidades de Podman sino las necesarias para reemplazar a Docker y adaptar su uso a otras herramientas como Docker Compose, que son muy utilizadas por la comunidad.

Docker Compose es una herramienta escrita en Python que nos permite definir aplicaciones con uno o más contenedores así como la relación entre ellos, a través de un fichero YAML. Es extremadamente útil al permitir a los desarrolladores crear entornos desechables y repetibles con un sólo comando.

Continuando con el ejemplo anterior, vamos a crear un entorno efímero de Traccar, formado por la aplicación y una base de datos. Pero antes necesitamos configurar Podman para que Docker Compose pueda usarlo como backend.

Docker Compose necesita lo siguiente para funcionar:
* Interactúa con el demonio de Docker y necesitamos que Podman se comporte igual, generando un socket al que Docker Compose pueda conectarse.
* La conectividad entre contenedores dentro de un stack de Docker Compose se realiza a través de una red interna, que resuelve el nombre del servicio que nosotros hemos definido en el YAML. 

Este último punto nos _obliga_ a utilizar contenedores con acceso root. Los contenedores _rootless_ tienen muchas limitaciones de red como no tener su propia IP y además Podman no ofrece por defecto resolución de nombres interna. La configuración recomendada de Podman obliga a los contenedores a comunicarse entre si a través de puertos expuestos en el host y requiere modificar nuestros ficheros de Docker Compose. Lo veremos un poco más adelante.

Los siguientes ajustes deben hacer tanto en nuestra distribución Linux como en la máquina virtual que Podman usa en Windows o Mac.

Lo primero es instalar una capa de compatibilidad entre Docker y Podman y las herramientas _podman-compose_ y _docker-compose_:

```bash
# El paquete podman-docker añade una serie de alias entre podman y docker para que podamos seguir utilizando los comandos de Docker
# aunque por debajo realmente se esté utilizando Podman. El nombre del paquete puede variar según la distribución Linux que estemos
# usando
sudo apt install podman-docker -y

# Después instalamos podman-compose y docker-compose
sudo pip3 install podman-compose
sudo pip3 install docker-compose

# Por último habilitamos el socket de Podman para que Docker Compose pueda conectarse a él sin problemas
sudo systemctl start podman.socket
```

Con esto resolvemos el primer inconveniente detectado para transicionar a Podman, pero para el último necesitamos modificar su configuración.

Aunque no es obligatorio, vamos a cambiar las políticas de acceso a cualquier registro de imágenes para que el funcionamiento de Podman sea similar al que tiene Docker por defecto.

```bash
# Instalamos una política de configuración de registros de contenedores por Defecto
sudo curl -L -o /etc/containers/registries.conf https://src.fedoraproject.org/rpms/containers-common/raw/main/f/registries.conf

# Modificamos la política descargada para habilitar el uso de nombres cortos en contenedores
sudo sed 's/enforcing/permissive/g' /etc/containers/registries.conf

# Instalamos la política de acceso a los registros
sudo curl -L -o /etc/containers/policy.json https://src.fedoraproject.org/rpms/containers-common/raw/main/f/default-policy.json
```

Ahora vamos a modificar las políticas de red utilizadas de Podman para permitir la resolución de contenedores por nombre. Para ello tenemos que modificar el fichero _/etc/cni/net.d/87-podman-bridge.conflist_, añadiendo las siguientes líneas:

![podman-cni](https://storage.googleapis.com/tangelov-data/images/0047-01.png)

También debemos instalar el plugin que habilita la resolución de nombres. En Ubuntu lo podemos hacer con el siguiente comando ```sudo cp /usr/lib/cni/dnsname /usr/lib/cni```, pero enn otras distribuciones como Fedora, es posible que necesitemos instalar un paquete extra llamado _podman-plugins_.

Una vez que ya lo hemos configurado bien, podemos empezar con Traccar. Necesitamos crear dos ficheros: uno que contiene la configuración de la base de datos y otro con la definición de los servicios para Docker Compose.

Nuestro primer fichero debe llamarse _traccar.xml_ y si nos fijamos en su contenido, le indicamos a Traccar que debe conectarse a una base de datos de nombre traccar en el host _mysql_:

```xml
<?xml version='1.0' encoding='UTF-8'?>

<!DOCTYPE properties SYSTEM 'http://java.sun.com/dtd/properties.dtd'>

<properties>
    <entry key='config.default'>./conf/default.xml</entry>

    <entry key='database.driver'>com.mysql.jdbc.Driver</entry>
    <entry key='database.url'>jdbc:mysql://mysql:3306/traccar?serverTimezone=UTC&amp;useSSL=false&amp;allowMultiQueries=true&amp;autoReconnect=true&amp;useUnicode=yes&amp;characterEncoding=UTF-8&amp;sessionVariables=sql_mode=''</entry>
    <entry key='database.user'>traccaruser</entry>
    <entry key='database.password'>traccarpassword</entry>

</properties>
```

El siguiente fichero es un fichero standard de Docker Compose, cuyo nombre debe ser _docker-compose.yml_:

```yaml
version: '2'
services: 

 mysql:
  image: mysql
  restart: always
  hostname: mysql
  environment:
   - MYSQL_ROOT_PASSWORD=my-super-secret-password
   - MYSQL_DATABASE=traccar
   - MYSQL_USER=traccaruser
   - MYSQL_PASSWORD=traccarpassword
  volumes:
   - mysql:/var/lib/mysql/

 traccar:
  image: traccar/traccar:4.13-debian
  hostname: traccar
  restart: always
  ports:
   - "5000-5150:5000-5150"
   - "8080:8082"
  volumes:
   - traccar-db:/opt/traccar/data/database
   - ./traccar.xml:/opt/traccar/conf/traccar.xml
  depends_on:
    - mysql

volumes:
 traccar-db:
 mysql:
```

Para la gente que no conozca Docker Compose, estamos definiendo dos servicios:
* El primero, de nombre _mysql_, utiliza la imagen oficial de MySQL en DockerHub y le asigna un volumen para tener persistencia en nuestra base de datos.
* El segundo, de nombre _traccar_, utiliza la imagen oficial de Traccar en DockerHub y fija su versión a la 4.13. También abre múltiples puertos al host y utiliza dos volúmenes: el primero guarda en local ciertos datos usados por Traccar y el segundo mapea el fichero de configuración que hemos creado antes dentro del contenedor.

Ahora sí, ya podemos probar nuestra instancia de Traccar con el comando ```sudo docker-compose up```:

```bash
sudo docker-compose up  
Creating network "test_default" with the default driver
Creating test_mysql_1 ... done
Creating test_traccar_1 ... done
Attaching to test_mysql_1, test_traccar_1
mysql_1    | 2022-03-26 11:20:40+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 5.7.37-1debian10 started.
mysql_1    | 2022-03-26 11:20:40+00:00 [Note] [Entrypoint]: Switching to dedicated user 'mysql'
mysql_1    | 2022-03-26 11:20:40+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 5.7.37-1debian10 started.
mysql_1    | 2022-03-26T11:20:41.177221Z 0 [Warning] TIMESTAMP with implicit DEFAULT value is deprecated. Please use --explicit_defaults_for_timestamp server option (see documentation for more details).
mysql_1    | 2022-03-26T11:20:41.178701Z 0 [Note] mysqld (mysqld 5.7.37) starting as process 1 ...
mysql_1    | 2022-03-26T11:20:41.393573Z 0 [Note] Server hostname (bind-address): '*'; port: 3306
mysql_1    | 2022-03-26T11:20:41.393599Z 0 [Note] IPv6 is available.
mysql_1    | 2022-03-26T11:20:41.393607Z 0 [Note]   - '::' resolves to '::';
mysql_1    | 2022-03-26T11:20:41.393618Z 0 [Note] Server socket created on IP: '::'.
mysql_1    | 2022-03-26T11:20:41.396472Z 0 [Warning] Insecure configuration for --pid-file: Location '/var/run/mysqld' in the path is accessible to all OS users. Consider choosing a different directory.
mysql_1    | 2022-03-26T11:20:41.403764Z 0 [Note] Event Scheduler: Loaded 0 events
mysql_1    | 2022-03-26T11:20:41.403973Z 0 [Note] mysqld: ready for connections.
mysql_1    | Version: '5.7.37'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server (GPL)
traccar_1  | Loading class `com.mysql.jdbc.Driver'. This is deprecated. The new driver class is `com.mysql.cj.jdbc.Driver'. The driver is automatically registered via the SPI and manual loading of the driver class is generally unnecessary.
```

Para destruir el entorno solo tenemos que ejecutar el comando ```sudo docker-compose down```.

### Podman en Windows o Mac OS
Como ya hemos comentado, Podman utiliza una máquina virtual para dar compatibilidad en sistemas operativos no-Linux. Por ello, antes de ejecutar cualquier contenedor, tenemos que crear dicha máquina.

Crear la máquina virtual es sencillo y requiere sólo de los siguientes pasos:

```bash
# Primero iniciamos la VM utilizada por Podman. En este paso es donde podemos configurar
# su tamaño, su almacenamiento, etc
podman machine init -v $HOME:$HOME

# Iniciamos la máquina virtual tras su creación
podman machine start

# Cambiamos la configuración de Podman para que la VM nos permita el uso de contenedores root
# para usar Docker Compose sin problemas
podman machine set --rootful

# Si hemos instalado Podman en Mac también recomendamos instalar el helper que viene incluido en la instalación
sudo /usr/local/Cellar/podman/$PODMAN_VERSION/bin/podman-mac-helper-install
```

Si vamos a utilizar Podman en Windows o Mac, recomiendo hacer todos los cambios de configuración del apartado anterior para facilitar su uso.

Estas versiones no nativas tienen algunas limitaciones que no me he encontrado en Linux:
* Ejecutan Podman en remoto, a través de una máquina virtual y nosotros interactuamos desde nuestro host contra dicha VM.
* El montaje de volúmenes da problemas y he sido incapaz de hacer que funciona en Windows, pese a que en teoría está bien soportado a través de WSL. Creo que es un bug temporal porque en versiones anteriores si que funcionaba.
* En ocasiones es necesario borrar a mano los volúmenes creados por Docker Compose puesto que Podman no los borra automáticamente al ejecutar docker-compose down.

> El error que me he encontrado parece una mala traslación del path de los ficheros entre Windows y el subsistema Linux que utiliza. Cuando esté solucionado actualizaré este post para que cualquiera pueda seguir la guía sin problemas.


### Podman Compose
Si la primera parte de este post se centraba en la evolución de Docker y la segunda en cómo adaptar Podman para que funcione como Docker, esta última parte se va a centrar en sus herramientas nativas: Podman Compose y Podman Desktop.

Podman Compose busca replicar las funcionalidades de su análogo y también soportar las características extra que Podman tiene. En este apartado vamos a ver cómo adaptar nuestros ficheros para que funcionen con Podman Compose sobre contenedores _rootless_.

Como ya he comentado, siempre que sea necesario debemos evitar el uso de contenedores con acceso root (aunque podríamos utilizar sudo) y debido a sus limitaciones, necesitamos hacer un par de cambios a nuestros ficheros:
* Primero mapeamos el puerto de MySQL al host para que otros contenedores puedan conectarse a él puesto que ya no va a tener una dirección IP propia.
* También modificamos el fichero XML de configuración para hacer que Traccar use la IP del host en lugar de la resolución por nombre típica de Docker.

El fichero de podman-compose sería el siguiente:

```yaml
# Fichero para podman-compose
version: '2'
services: 

 mysql:
  image: mysql
  restart: always
  ports:
   - "3306:3306"
  hostname: mysql
  environment:
   - MYSQL_ROOT_PASSWORD=my-super-secret-password
   - MYSQL_DATABASE=traccar
   - MYSQL_USER=traccaruser
   - MYSQL_PASSWORD=traccarpassword
  volumes:
   - mysql:/var/lib/mysql/

 traccar:
  image: traccar/traccar:4.13-debian
  hostname: traccar
  restart: always
  ports:
   - "5000-5150:5000-5150"
   - "8080:8082"
  volumes:
   - traccar-db:/opt/traccar/data/database
   - ./traccar.xml:/opt/traccar/conf/traccar.xml
  depends_on:
    - mysql

volumes:
 traccar-db:
 mysql:
```

Y el fichero de configuración quedaría así:

```xml
<?xml version='1.0' encoding='UTF-8'?>

<!DOCTYPE properties SYSTEM 'http://java.sun.com/dtd/properties.dtd'>

<properties>
    <entry key='config.default'>./conf/default.xml</entry>

    <entry key='database.driver'>com.mysql.jdbc.Driver</entry>
    <entry key='database.url'>jdbc:mysql://${IP_DEL_HOST}:3306/traccar?serverTimezone=UTC&amp;useSSL=false&amp;allowMultiQueries=true&amp;autoReconnect=true&amp;useUnicode=yes&amp;characterEncoding=UTF-8&amp;sessionVariables=sql_mode=''</entry>
    <entry key='database.user'>traccaruser</entry>
    <entry key='database.password'>traccarpassword</entry>

</properties>
```

Con los nuevos cambios podemos ejecutar ```podman-compose up```y tendremos un resultado similar al anterior pero con mucha más seguridad para el usuario que esté desarrollando o haciendo pruebas.

### Podman Desktop
A diferencia de Docker, Podman y su ecosistema no tienen una interfaz gráfica oficial que podamos usar. Por ello, la comunidad está desarrollando varias alternativas que mejoran la experiencia de uso. De todas ellas la más avanzada actualmente es _Podman Desktop_.

![podman-desktop](https://storage.googleapis.com/tangelov-data/images/0047-02.png)

Podman Desktop es una aplicación basada en Electron (sin soporte para Windows por el momento) que nos permite administrar nuestras imágenes y contenedores a través de una interfaz gráfica. Algunas de sus funcionalidades son las siguientes:
* Controlar los contenedores que tenemos en ejecución: ver sus logs en pantalla, acceder a la terminal de los mismos o al puerto que tengan abierto, reiniciarlos, etc.
* Gestionar las imágenes de contenedores que tengamos en local, pushearlas a un repositorio remoto, etc.
* Configurar la VM que utiliza en sistemas no Linux.
* Gestionar los volúmenes y los secretos.

Se espera que el número de funcionalidades vaya aumentando en el tiempo aunque por el momento ya cubre gran parte de las que proporciona Docker Desktop.

Poco más que añadir, os animo a que probéis Podman y que vuestra experiencia sea tan productiva como la mía. Un saludo a todos y nos vemos en el siguiente post.


## Documentación

* [What are containers (ENG)](https://mattjhayes.com/2018/03/09/containers-part-1-what-are-containers/)

* [List of OS-level virtualization in Wikipedia (ENG)](https://en.wikipedia.org/wiki/OS-level_virtualization#Implementations)

* [How Docker broke in half (ENG)](https://www.infoworld.com/article/3632142/how-docker-broke-in-half.html)

* [Mirantis aquires Docker Enterprise (ENG)](https://techcrunch.com/2019/11/13/mirantis-acquires-docker-enterprise/)

* Docker product changes (ENG): [I](https://www.docker.com/blog/scaling-dockers-business-to-serve-millions-more-developers-storage/?utm_source=thenewstack&utm_medium=website&utm_campaign=platform), [II](https://www.docker.com/blog/updating-product-subscriptions/) and [III](https://www.docker.com/blog/the-grace-period-for-the-docker-subscription-service-agreement-ends-soon-heres-what-you-need-to-know/)

* [Podman, with Daniel Walsh and Brent Baude (ENG)](https://kubernetespodcast.com/episode/164-podman/)

* [Why Red Hat is investing in CRI-O and Podman (ENG)](https://www.redhat.com/en/blog/why-red-hat-investing-cri-o-and-podman)

* [Official Documentation of Docker Compose (ENG)](https://docs.docker.com/compose/)

* [Favoring Podman over Docker Desktop (ENG)](https://medium.com/@butkovic/favoring-podman-over-docker-desktop-33368e031ba0)

* [Podman Desktop (ENG)](https://iongion.github.io/podman-desktop-companion/)

Revisado a 01-05-2023

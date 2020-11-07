---
title: "Ansible (II): nuestro primer playbook"
slug: "ansible-ii"
authors:
  - tangelov
date: 2018-02-28T18:00:00+02:00
tags:  ["ansible", "python"]
categories: ["devops"]
draft: false
---

Generalmente cualquier _sysadmin_ termina acumulando una serie de scripts que le facilitan la vida. En casa tengo una pequeña _motherboard_, una prima lejana de la Raspberri Pi que incluía un puerto SATA2 y un Gigabit Ethernet. Así que lo convertí en un pequeño NAS que utilizo de "nube" privada.

Aunque existían opciones más simples, terminé instalándole [Nextcloud](https://www.nextcloud.com), un fork de Owncloud y lo utilizo para sincronizar ficheros con mis PCs.

Para que el coste en tiempo del mantenimiento fuera mínimo, terminé desarrollando tres scripts que lo hacían "todo" por mi:

* Un script que realiza los backups de la máquina.

* Un script que actualiza el software de la máquina de manera automática y segura.

* Un script que se encarga de subir el fichero resultante del backup a un Google Drive.

En este post y en el siguiente, voy a explicar el paso a paso de cómo he transformado el primer script en un rol de Ansible que pueda ser utilizado por otros fácilmente.

<!--more-->

## Primeros pasos
En primer lugar voy a explicar el script original. Podeis verlo [aquí](https://gitlab.com/tangelov/scripts/blob/master/old/old_nxtcloud_maintenance.sh).

El script realiza un backup completo de todas las partes que necesitaríamos en caso de tener que reconstruir el servidor: directorio web, directorio de datos, bases de datos asociadas, archivos de configuración de los servicios de la máquina, etc. Por simple comodidad, el backup es completo y no incremental. Consta de los siguientes pasos:

* Generamos un directorio temporal donde almacenamos una copia de todos los archivos del web server, de los datos de los usuarios y realizamos un volcado de las bases de datos del servidor.

* Copiamos los archivos de configuración de los servicios importantes (PHP, MySQL, Nginx, etc)

* Generamos un archivo comprimido con la carpeta temporal antes generada

* Lo ciframos con GPG

El script simplemente funciona, pero no necesitaba hacerlo, puesto que puedo gestionar los pasos que realiza de forma sencilla gracias a _backupninja_. Es una herramienta que se encuentra en todos los repositorios y que nos permite gestionar paso a paso las copias de manera sencilla.

## Creación del rol
Para crear el rol no debemos sólo instalar el paquete sino también conocer un poco la estructura interna de backupninja. Dicha herramienta tiene dos tipos de ficheros de configuración:

* Una general para el servicio localizada en _/etc/backupninja.conf_

* Una carpeta (_/etc/backup.d/_) donde se almacenan todos los pasos que se van a realizar durante el backup. Cada uno de estos ficheros empiezan por un número y si éste es el 0, significa que están desactivados.

Con esto en mente vamos a comenzar con nuestro rol y utilizamos el comando ``ansible-galaxy init backupninja`` para que la propia herramienta nos genere la estructura de ficheros yaml y carpetas que debe tener un rol. Nuestro nuevo rol se parecerá a esto:

```bash
[tangelov@portatil backupninja] $ tree 
.
├── defaults
│   └── main.yml
├── files
├── handlers
│   └── main.yml
├── meta
│   └── main.yml
├── README.md
├── tasks
│   └── main.yml
├── templates
├── tests
│   ├── inventory
│   └── test.yml
└── vars
    └── main.yml
```

Cada carpeta tiene una función:

* _defaults_: Almacena los valores que queramos que ciertas variables tengan por defecto. Por ejemplo, yo lo utilizo para colocar todas las variables personalizables a la hora de ejecutar el rol.

* _files_: son ficheros que pueden ser desplegados con este rol. Si queremos copiar un fichero estático, es la forma de la que debemos hacerlo.

* _handlers_: son determinadas acciones que se ejecutan únicamente cuando alguna tarea ha provocado un cambio en la configuración.

* _meta_: es un directorio para añadir metadatos al rol. También podemos usarlo para indicar las dependencias, licencias y comentarios del rol.

* _tasks_: Contiene las diferentes tareas que va a realizar nuestro rol.

* _templates_: Contiene plantillas escritas en formato Jinja2 que podremos personalizar con variables de manera dinámica.

* _tests_: Se almacenan los tests de infraestructura que prueban nuestro rol en un entorno de laboratorio.

* _vars_: Es una carpeta donde podemos almacenar variables (no es el único sitio donde podemos hacerlo)

Ya en el siguiente post sobre el tema, empezaremos a crear nuestro rol.


## Documentación

* [Estructura de un rol (ENG)](http://docs.ansible.com/ansible/latest/playbooks_reuse_roles.html)

* [Gitlab de Backupninja (ENG)](https://0xacab.org/riseuplabs/backupninja)

Revisado a 01/02/2020

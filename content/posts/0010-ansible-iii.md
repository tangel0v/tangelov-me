---
title: "Ansible (III): roles y templates"
slug: ansible-iii
authors:
  - tangelov
date: 2018-07-26T10:00:00+02:00
tags:  ["ansible", "python"]
categories: ["devops"]
draft: false
---

Tras una breve pausa derivada del hecho de que me he _casado_ :D, seguimos apuntando cosillas en el blog. En este artículo vamos a crear un pequeño rol que nos permita gestionar nuestros backups como debería ser.

Ya comentamos en el post anterior, todo lo que hacía el [script](https://tangelov.me/posts/ansible-ii.html) y ahora vamos a crear el rol

<!--more-->

## Instalación de Backupninja
Nuestro rol va a realizar principalmente dos acciones: en una va a instalar backupninja y en la segunda le va a aplicar la configuración que nosotros queremos. Así que nos vamos al fichero _tasks/main.yml_ y comenzamos a editarlo:

```yaml
---
# tasks file for backupninja

- name: Install backupninja package
  package:
    name: backupninja
    state: present
```

Ese conjunto de líneas serían una tarea completa. El formato yaml utilizado por Ansible no necesita usar paréntesis puesto que determina a que pertenece cada línea en función de la indentación. Vamos a proceder a explicarlo:

* _name_: El primer _name_ se corresponde al nombre que tiene la tarea y que se va a mostrar en la terminal cuando ejecutemos el rol.

* _package_: Se corresponde con el nombre del módulo de Ansible que estamos utilizando. En este caso, package es módulo que nos permite instalar paquetes sin importar de que distribución GNU/Linux estemos utilizando. Podemos ver más información [aquí](https://docs.ansible.com/ansible/2.9/modules/package_module.html). Cada módulo recibe una serie de parámetros para funcionar y en este caso le pasamos el nombre del paquete y el estado en el que queremos que esté (_present_ significa que el paquete se instalará en caso de no estarlo).


## Plantillas
Nuestro rol ya instalaría backupninja y ahora vamos a preparar las plantillas con nuestra configuración en ../templates. Ansible utiliza Jinja2 para las plantillas así que deberemos conocer su sintaxis aunque es bastante intuitiva.

Voy a crear la plantilla tar.j2 basándonos en los ficheros de configuración que crea backupninja como ejemplo.

```jinja2
# {{ ansible_managed }}

when = everyday at 02

backupname = "bananapi"
backupdir = "/media/disk/backup/tmp"

compress = gzip

includes = "/media/disk/datos /var/www/nextcloud"
excludes = "/tmp /proc /sys /dev /srv /misc /net /selinux"

DATEFORMAT = %Y.%m.%d
```

Este fichero de configuración crearía un backup a las dos de la mañana, con el nombre de _bananapi_ y un formato de fecha YYYY.MM.dd en el directorio _/media/disk/backup/tmp_ con el contenido de los directorios _/media/disk/datos y /var/www/nextcloud_ . También añadiría un comentario en la primera línea imprimiendo la variable _ansible_managed_ . En Jinja2 las variables se utilizan entre dobles llaves.

Aunque esta plantilla sería funcional para nuestras necesidades, no le serviría a otros así que vamos a utilizar más variables. Ahora nuestra plantilla _tar.j2_ sería así:

```jinja2
# {{ ansible_managed }}

when = {{ ninja_when }}

backupname = {{ ninja_backupname }}
backupdir = {{ ninja_backupdir }}

compress = {{ ninja_compress }}

includes = {{ ninja_includes }}
excludes = {{ ninja_excludes }}

DATEFORMAT = %Y.%m.%d
```

## Despliegue de la configuración
Tras crear la plantilla ahora debemos crear una nueva tarea que despliegue la configuraciónn y para ello volvemos a editar el fichero _~/tasks/main.yml_

```yaml
---
# tasks file for backupninja

- name: Install backupninja package
  package:
    name: backupninja
    state: present

- name: Deploy TAR template
  template:
    src: tar.j2
    dest: "/etc/backup.d/10.tar"
    mode: '0600'
    owner: root
    group: root
```

En este caso hemos añadido una nueva tarea que utiliza el módulo _template_ y crea un fichero 10.tar en /etc/backup.d/ utilizando la plantilla tar.j2 como fuente. El fichero además tendrá permisos 600 y pertenecerá a root:root.


## Variables
La plantilla que hemos creado antes tiene variables declaradas que no han sido definidas en ningún sitio por lo que si ahora desplegáramos la configuración ésta no sería la correcta. Ansible soporta variables de muchísimas maneras y recomendamos leer su [documentación](https://docs.ansible.com/ansible/2.9/user_guide/playbooks_variables.html). En nuestro caso vamos a definir ciertas variables en el ~/defaults/main.yml:

```jinja2
ninja_when: "everyday at 02"
ninja_backupname: ""
ninja_backupdir: ""
ninja_compress: "gzip"
ninja_includes: ""
ninja_excludes: "/tmp /proc /sys /dev /srv /misc /net /selinux"
```

Como se puede observar, he declarado todas las variables aunque no todas tienen un valor. He pretendido darles un valor sólo a las variables que suelen mantenerse entre servidores aunque pueden ser sobreescritas sin necesidad de modificar el rol. Debemos recordar que en la medida de lo posible un rol debe ser independiente del servidor en el que se vaya a instalar.


## Ejecución del rol
Ahora ya tenemos una pequeña versión preliminar de una parte del rol y vamos a proceder a ejecutarla desde un playbook. De esta forma nos vamos a la carpeta padre del rol y creamos dos ficheros: uno para nuestro playbook (test-backupninja.yml) y otro con variables (test-backupninja-vars.yml).

```yml
---
- name: Backupninja test
  hosts: banana
  become: true

  pre_tasks:
    - include_vars: "test-backupninja-vars.yml"

  roles:
    - backupninja
```

Como vemos en el archivo de variables cambiamos el valor de ninja_when para sobreescribir el que viene por defecto.

```yaml
---
ninja_when: "everyday at 01"
ninja_backupname: "bananapi"
ninja_backupdir: "/media/disk/backup/tmp"
ninja_includes: "/media/disk/datos /var/www/nextcloud"
ninja_excludes: "/tmp /proc /sys /dev /srv /misc /net /selinux"
```

En el primer YAML añadimos las variables que nos faltan mediante el módulo include_tasks y después ejecutamos el rol. Vamos a probarlo y a ver el resultado:

```bash
ansible-playbook -i hosts test-backupninja.yml 

PLAY [Backupninja test] **********************************************************************

TASK [Gathering Facts] ***********************************************************************
ok: [banana]

TASK [include_vars] **************************************************************************
ok: [banana]

TASK [backupninja : Install backupninja packages] ********************************************
ok: [banana] => (item=backupninja)

TASK [backupninja : Deploy TAR template] *****************************************************
changed: [banana]

PLAY RECAP ***********************************************************************************
banana                     : ok=4    changed=1    unreachable=0    failed=0   
```

Como resultado de la ejecución podemos ver que Backupninja ya estaba instalado y que se ha producido un cambio en la plantilla y si nos logueamos podemos ver que se ha desplegado de forma correcta (sustituyéndose el _when_ a "everyday at 01").

```jinja2
# Ansible managed

when = everyday at 01

backupname = bananapi
backupdir = /media/disk/backup/tmp

compress = gzip

includes = /media/disk/datos /var/www/nextcloud
excludes = /tmp /proc /sys /dev /srv /misc /net /selinux

DATEFORMAT = %Y.%m.%d
```

Hasta aquí llegamos con el despleigue del rol de Backupninja. En la próxima entrega añadiremos dos pasos más y configuraremos el rol para que sea multi-distribución.


## Documentación

* [Estructura de un rol (ENG)](https://docs.ansible.com/ansible/2.9/user_guide/playbooks_reuse_roles.html)

* [Gitlab de Backupninja (ENG)](https://0xacab.org/riseuplabs/backupninja)

* [Plantillas en Jinja2 (ENG)](https://jinja.palletsprojects.com/en/2.11.x/templates/)

* [Orden de preferencia de variables en Ansible (ENG)](https://docs.ansible.com/ansible/2.9/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable)


Revisado a 01/03/2021

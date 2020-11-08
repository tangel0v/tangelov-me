---
title: "Ansible (IV): mejorando nuestros roles"
slug: ansible-iv
authors:
  - tangelov
date: 2018-08-01T07:00:00+02:00
tags:  ["ansible", "python"]
categories: ["devops"]
draft: false
---

Como comentamos en el post [anterior](https://tangelov.me/posts/ansible-iii.html), ahora vamos a proceder a añadir dos pasos extra a nuestro rol de backupninja y a implementar una primera mejora haciendo que el rol sea válido para muchas más distribuciones GNU/Linux. En definitiva:

* Nuestro rol ya instala backupninja y le permite realizar un backup completo de los datos del servidor.

* Necesitamos añadirle el backup de las bases de datos y realizar un paquete de ambos para obtener el backup definitivo. 

<!--more-->

## Nuevas plantillas
Cada paso extra en Backupninja se corresponde con una plantilla nueva siendo ordenadas en función del número con el que comienza el fichero de configuración. De esta forma si tengo tres plantillas con los nombres _10.tar_, _20.mysql_ y _30.tar_, se ejecutarán en el orden de 10, 20 y 30.

Volvemos a la carpeta que contiene nuestro rol y creamos la plantilla Jinja2 para MySQL con el nombre _mysql.j2_ en la carpeta _templates_ :

```jinja2
# {{ ansible_managed }}

# make a backup of the actual binary files using mysqlhotcopy.
hotcopy = {{ ninja_mysql_hotcopy }}

# make a backup using mysqldump. this creates text files with sql
# commands sufficient to reconstruct the database.
sqldump = {{ ninja_mysql_sqldump }}

# compress - if yes, compress the sqldump output
compress = {{ ninja_mysql_compress }}

# host co connect to do the backups (localhost: default)
dbhost = {{ ninja_mysql_dbhost }}

# backupdir - hotcopy backups will be in a subdirectory called sqldump
backupdir = {{ ninja_mysql_backupdir }}

# databases - which databases to backup. it should be 'all' or
# a space separated list of database names.
databases = {{ ninja_mysql_databases }}

configfile = /etc/mysql/debian.cnf
```

El último paso a realizar sería comprimir todos los datos en un nuevo archivador, pero ya tenemos una plantilla que podemos usar para eso. Ahora veremos como hacerlo, pero primero añadimos las siguientes variables en _~/defaults/main.yml_:

```jinja2
ninja_mysql_hotcopy: "no"
ninja_mysql_sqldump: "yes"
ninja_mysql_compress: "yes"
ninja_mysql_dbhost: "localhost"
ninja_mysql_backupdir: ""
ninja_mysql_databases: "all"
```


## Nuevas tareas
Una vez ya hemos completado nuestras plantillas vamos a añadir su despliegue al fichero de tareas, quedando así:

```jinja2
---
# tasks file for backupninja

- name: Install backupninja packages
  package:
    name: "{{ item }}"
    state: present
  with_items:
    - backupninja

- name: Deploy TAR template
  template:
    src: tar.j2
    dest: "/etc/backup.d/10.tar"
    mode: '0600'
    owner: root
    group: root

- name: Backup MySQL
  template:
    src: mysql.j2
    dest: "/etc/backup.d/20.mysql"
    mode: '0600'
    owner: root
    group: root

- name: Prepare variables for last tar template
  set_fact:
    ninja_backupname: "{{ ninja_backupname_def }}"
    ninja_includes: "{{ ninja_backupdir }}"
    ninja_backupdir: "{{ ninja_backupdir_def }}"

- name: Deploy full TAR template
  template:
    src: tar.j2
    dest: "/etc/backup.d/30.tar"
    mode: '0600'
    owner: root
    group: root
```

Como podemos ver, estamos utilizando la misma plantilla para desplegar dos pasos diferentes. Para el segundo caso necesitamos configurar algunas variables de nuevo y por ello hemos introducido una nueva tarea con el módulo [set_fact](https://docs.ansible.com/ansible/latest/modules/set_fact_module.html). Estas nuevas variables tendremos que configurarlas en el playbook que lanza el rol.


## Lanzando de nuevo el playbook
Como en el post anterior, vamos a añadir las nuevas variables al playbook dejando el fichero así:

```yaml
---
ninja_when: "everyday at 02"
ninja_backupname: "bananapi"
ninja_backupdir: "/media/disk/backup/tmp"
ninja_includes: "/media/disk/datos /var/www/nextcloud"
ninja_excludes: "/tmp /proc /sys /dev /srv /misc /net /selinux"

ninja_mysql_backupdir: "{{ ninja_backupdir }}"

ninja_backupname_def: "bananapi-def"
ninja_backupdir_def: "/media/disk/backup"
```

Y ahora procedemos a lanzarlo: ansible-playbook test-backupninja.yml

```bash

PLAY [Backupninja test] **********************************************************************

TASK [Gathering Facts] ***********************************************************************
ok: [banana]

TASK [include_vars] **************************************************************************
ok: [banana]

TASK [backupninja : Install backupninja packages] ********************************************
ok: [banana] => (item=backupninja)

TASK [backupninja : Deploy TAR template] *****************************************************
ok: [banana]

TASK [backupninja : Backup MySQL] ************************************************************
changed: [banana]

TASK [backupninja : Prepare variables for last tar template] *********************************
changed: [banana]

TASK [backupninja : Deploy full TAR template] ************************************************
changed: [banana]

PLAY RECAP ***********************************************************************************
banana                     : ok=4    changed=3    unreachable=0    failed=0   

```

Si miramos en el servidor, podemos ver que el despliegue ha sido correcto:

![Ficheros de configuración](https://storage.googleapis.com/tangelov-data/images/0011-00.png)

Ahora vamos a ejecutar backupninja con _backupninja -n_ y también podemos ver que se ha creado el paquete con todo :D

```bash
root@banana:/media/disk/backup# ls -lah
total 10G
drwxr-xr-x 3 root root 4.0K Jul 28 11:40 .
drwxr-xr-x 5 root root 4.0K Nov 31  2017 ..
-rw------- 1 root root   49 Jul 28 11:40 bananapi-def-2018.07.28.err
-rw------- 1 root root   71 Jul 28 11:40 bananapi-def-2018.07.28.list
-rw------- 1 root root 501M Jul 28 11:44 bananapi-def-2018.07.28.tgz
```

## Aprovechando Ansible
En este punto, nuestro rol de Ansible soporta todas las características que tenía el viejo script en bash. Sin embargo, Ansible nos proporciona un potencial de mejora enorme. De caja ya nos proporciona idempotencia que garantiza que nuestra configuración sea siempre la adecuada, pero vamos a ir tuneando nuestro rol para hacerlo más potente y profundizar.

La última parte del post va a añadir soporte para otras distribuciones: en este caso CentOS, Fedora y Red Hat, es decir las principales distribuciones con paquetería RPM.

Nuestro rol en este punto tiene dos posibles puntos de conflicto:

* La instalación del paquete backupninja. En muchas ocasiones los nombres de los paquetes cambian según la distribución. En este caso el nombre se mantiene entre todas ellas, pero se encuent
ra en un repositorio extra que debemos habilitar con una nueva tarea que sólo se aplicará si la distribución es la correcta.

* La realización del backup de MySQL. Si revisamos el código de la plantilla de MySQL veremos que estamos haciendo el backup utilizando el usuario que crea Debian para mantenimiento y dicho usuario no va a existir en CentOS y cia así que vamos a arreglarlo.

### Plantillas multi-distribución
Hemos realizado la siguiente modificación a la plantilla de MySQL:

```jinja2
{% if ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu' %}
configfile = /etc/mysql/debian.cnf
{% endif %}
{% if ansible_distribution == 'CentOs' or ansible_distribution == 'Red Hat Enterprise Linux' or ansible_distribution == 'Fedora' %}
dbusername = {{ ninja_mysql_username }}
dbuserpassword = {{ ninja_mysql_userpassword }}
{% endif %}
```

Hemos añadido una serie de condicionales a la plantilla que sólo se escribirán en el fichero si la condición se cumple. De esta forma en el caso de utilizar una distribución basada en RPM tendríamos que utilizar unas nuevas variables que se corresponden con el usuario y contraseña que backupninja debe usar para conectarse al servidor.

### Tareas multidistribución
Debemos añadir una una tarea al rol que permita a los usuarios de las distribuciones basadas en RPM (Red Hat, Fedora y CentOS) descargarse el paquete backupninja y lo vamos a hacer añadiendo el repositorio EPEL gracias al uso del módulo _yum repository_. Hemos añadido una nueva tarea en nuestro rol con el siguiente contenido:

```yaml
# tasks file for backupninja
- name: Install EPEL repository if needed
  yum_repository:
    name: EPEL YUM repo
    baseurl: https://download.fedoraproject.org/pub/epel/$releasever/$basearch/
    enabled: yes
    gpgcheck: yes
    gpgkey: https://download.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-7
  when: ansible_distribution == "CentOS" or ansible_distribution == "Red Hat Enterprise Linux" or ansible_distribution == "Fedora"
```

Esta tarea tiene una característica nueva que no tenían las anteriores y es una condición. Al añadir _when_ a una tarea, ésta sólo se ejecutará si se cumple dicha condición. En este caso sólo lo hará si se ejecuta en un ordenador que tenga instalado CentOS, RHEL o Fedora.


Con esto podemos dar por terminado este post. En el siguiente vamos a mostrar cómo probar nuestros roles en diferentes entornos gracias a molecule.

Muchas gracias.


## Documentación

* [Estructura de un rol (ENG)](http://docs.ansible.com/ansible/latest/playbooks_reuse_roles.html)

* [Gitlab de Backupninja (ENG)](https://0xacab.org/riseuplabs/backupninja)

* [Plantillas en Jinja2 (ENG)](https://jinja.palletsprojects.com/en/2.10.x/templates/)

* [Orden de preferencia de variables en Ansible (ENG)](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable)

Revisado a 01/02/2020

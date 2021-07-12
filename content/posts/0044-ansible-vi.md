---
title: "Ansible (VI): El camino hacia Ansible 2.11"
slug: ansible-vi
authors:
  - tangelov
date: 2021-07-11T10:00:00+02:00
tags:  ["ansible", "python"]
categories: ["devops"]
draft: false
---

Ansible siempre ha sido mi gestor de configuración favorito. Al utilizar _yaml_, siempre me pareció una herramienta con poca curva de aprendizaje y mucho potencial (no me equivocaba).

Hacía mucho que no escribía sobre Ansible: aunque no he dejado de utilizarlo, mi carrera profesional se ha orientado más hacia contenedores y sistemas serverless. A día de hoy, sigue formando parte de mi día a día a nivel personal puesto que lo sigo utilizando para realizar pruebas y para mantener todos los servidores que administro fuera de mi horario laboral. También mantengo un rol de Ansible para ayudarme en dicha tarea.

A pesar de mi silencio, Ansible ha continuado creciendo y ha sufrido una gran transformación durante estos años, de la cual no he estado desconectado. En este post vamos a revisar cuales han sido dichos cambios y cómo adaptar nuestros playbooks y roles a ellos.

<!--more-->

## Cambios en Ansible
Desde el comienzo, la popularidad de Ansible fue bastante alta, pero a partir de su versión 2.0, ésta explotó. A medida que crecía la comunidad y los casos de uso, Ansible amplió muchísimo su rango de acción y su número de módulos no dejó de crecer. Actualmente podemos utilizar Ansible para casi todo: configurar hosts de VMWare, elementos de red, interaccionar con contenedores en Kubernetes o crear infraestructura en la nube.

Aunque Red Hat es la compañía encargada principalmente del desarrollo de Ansible, parte de sus módulos son desarrollados y mantenidos por terceros (proveedores, particulares, etc) y al haber nacido como un proyecto mucho más pequeño, su modelo de gestión era el siguiente:

1. Cada vez que un bug era detectado en alguna parte de la herramienta, éste era creado como _Issue_ en el único repositorio central que existía.

2. Tras verificar que el bug era real, éste debía ser asignado al equipo encargado de solucionarlo. Aunque Red Hat sólo da soporte a una parte de los módulos de Ansible, si realizaba este tipo de gestiones y el uso de un repositorio centralizado creó rápidamente un volumen de _Issues abiertas_ tan alto que se convirtió en un cuello de botella.

3. Una vez asignado al equipo correcto, éste arreglaba el bug y era incluido en alguna de las versiones futuras de Ansible.

Las dificultades del modelo fueron muy evidentes: 

* No escalaba bien: a mayor popularidad de la herramienta, mayor número de _issues_ y mayor volumen de gestión.

* No era ágil: cualquier bug debía de pasar todo el proceso de validación y no era posible actualizar módulos de terceros de forma independiente.

* No era claro: cuando se detectaba un bug, era difícil saber quien era el encargado de solucionarlo y podía generarse mucho ruido durante el proceso.

Todo ello hizo que el sistema de gestión de Ansible cambiara. A partir de la versión _2.10_, sólo los módulos oficiales estarían integrados en el repositorio oficial y el resto tendrían que ser descargados externalmente a través de un nuevo tipo de elemento llamado _collections_. El uso de colecciones permitiría:

* Descongestionar el repositorio de Ansible, permitiendo redirigir automáticamente los bugs a sus respectivos grupos de soporte (Red Hat, comunidad y proveedores).

* Actualizar los módulos y corregir bugs de forma independiente a la CLI de Ansible.

Basándose en este cambio, también se crearían dos nuevas versiones de Ansible: la 3.0 que evolucionaría desde la 2.10 y la 4.0 que lo haría desde 2.11.

### Las colecciones y la nueva sintaxis de Ansible
Las _collections_ o colecciones son una _nueva_ forma de distribución de playbooks, roles, módulos o plugins dentro del ecosistema de Ansible. Gran parte de los módulos que anteriormente estaban integrados en el core, ahora forman parte de colecciones (como los módulos para crear usuarios o bases de datos en MySQL) y es necesario instalarlos previamente para poder utilizarlos.

Antes de nada, me gustaría comentar que para instalar Ansible 2.10 o superiores, es necesario desinstalar previamente la versión anterior:

```bash
# Desinstalando cualquier versión de Ansible 2.9 o inferiores
pip3 uninstall ansible --user

# Instalando la versión 2.10 de Ansible
pip3 install ansible-base --user

# O instando la versión 2.11 de Ansible. Son incompatibles entre si, por lo que si alguien va a utilizar las dos, le recomiendo que use venvs
pip3 install ansible-core --user

# También podemos instalar Ansible 3 o 4, pero realmente estaríamos instalando Ansible 2.11 o 2.12 respectivamente
```

Una vez tenemos una versión más actual de Ansible, la gestión de colecciones es muy parecida a la de roles: pueden descargarse de cualquier repositorio de código o de Ansible Galaxy, utilizando la CLI o a través del fichero de dependencias _requirements.yml_:

```yaml
---
collections:
  - name: community.general
    version: 3.2.0
roles:
  - src: gantsign.oh-my-zsh
    version: 2.3.0
```

Para añadir una colección, tan sólo tenemos que añadir una nueva clave, llamada _collections_, indicar el nombre de la misma y su versión. Tras ser añadida al fichero, ahora podríamos instalar dichas colecciones con el siguiente comando: ```ansible-galaxy collection install -r requirements.yml```.

La aparición de las colecciones hizo que fuese necesario transformar la sintaxis que Ansible había utilizado hasta entonces. Como no todos los módulos se cargaban desde el core, era necesario referenciarlos de otra manera. Cualquier módulo que se encontrase en una colección de terceros pasaba a ser llamado como si fuese un rol. Si en la versión 2.4 de Ansible la sintaxis a utilizar sería ésta:

```yaml
- name: Updating root password to a new one
  mysql_user:
    name: root
    config_file: '/etc/mysql/debian.cnf'
    password: "{{ mysql_root_user_password }}"
    priv: "*.*:ALL,GRANT"
    host_all: yes
  ignore_errors: yes
```

En cualquier versión de Ansible posterior a la 2.9 sería así:

```yaml
- name: Updating root password to a new one
  community.mysql.mysql_user:
    name: root
    config_file: '/etc/mysql/debian.cnf'
    password: "{{ mysql_root_user_password }}"
    priv: "*.*:ALL,GRANT"
    host_all: yes
  ignore_errors: yes
```

Para ejecutar cualquier módulo, ahora debemos referenciar la colección a la que éste pertenece junto a su nombre. Aunque los módulos del core de Ansible (como _file_, _template_, _command_) pueden continuar utilizando la sintaxis anterior, recomiendo utilizar el nuevo formato para irnos acostumbrando a él.

El proceso de migración de nuestros playbooks y roles a versiones posteriores a Ansible 2.9 consta de los siguientes pasos:

1. Identificar a que colección pertenencen los módulos que utilizamos y añadirlas a nuestro fichero de _requirements.yml_.

2. Modificar las tareas para que referencien a las colecciones y verificar si ha habido cambios en los parámetros de cada uno de los módulos que contienen.

Así ha quedado en mi caso uno de mis playbooks tras realizar todos los cambios:

```yaml
- hosts: "raspberri"
  vars_files:
    - "vaults/{{ inventory_hostname }}-vault.yml"
    - "../vars.yml"

  tasks:
  - name: Installation of basic utils
    ansible.builtin.import_tasks: tasks/common.yml

  - name: Installation of common web dependencies
    become: true
    tags: webserver
    block:
      - name: Installation of PHP dependencies
        tags: php
        ansible.builtin.import_tasks: tasks/php.yml

      - name: Importing of Nginx and Letsencrypt tasks
        ansible.builtin.import_tasks: tasks/web.yml

      - name: Installation of MySQL dependencies
        tags: mysql
        ansible.builtin.import_tasks: tasks/mysql.yml

  - name: Installing Nextcloud
    become: true
    tags: nextcloud
    vars:
      mount_point: "{{ vault_mount_point }}"
      mount_disk: "{{ vault_mount_disk }}"
      mount_disk_fs: "{{ vault_mount_disk_fs }}"
    block:
      - name: Creating directory to mount disk
        ansible.builtin.file:
          path: "{{ mount_point }}"
          owner: "root"
          group: "root"
          mode: 0755
          state: directory

      - name: Mounting disk and adding to fstab
        ansible.posix.mount:
          path: "{{ mount_point }}"
          src: "{{ mount_disk }}"
          fstype: "{{ mount_disk_fs }}"
          state: mounted

      - name: Installation of Nextcloud
        tags: nextcloud
        ansible.builtin.import_tasks: tasks/nextcloud.yml
``` 

Este playbook utiliza dos colecciones diferentes: _ansible.builtin_, que contiene cualquier módulo del core de Ansible y _ansible.posix_, que es donde se encuentran los módulos para gestionar discos y particiones. Si alguien está interesado en ver todos los cambios, puede hacer click [aquí](https://gitlab.com/tangelov/configuration/-/commit/b4175a90f7078bc1bbb0fe27098e67a561d0e18d) para ver más detalle.

La migración fue todo un éxito y aunque no voy a citar en detalle todos los cambios, si me gustaría comentar algunos que me han resultado llamativos:

* El número de colecciones que uso es mucho menor de lo que me esperaba. Sólo utilizo tres y la inmensa mayoría de los módulos se encuentran en el _core_.

* El módulo _file_ ahora requiere la instalación del paquete _acl_ (en sistemas basados en Debian). No se si es una mejora o una dependencia que se me había traspapelado en el pasado.

* El módulo _get\_url_ ya no requiere especificar _remote\_src_ como parámetro. Se entiende que las URLs son por defecto externas.


## Podman y Molecule: testeando roles de Ansible en 2021
Junto a la CLI, el ecosistema de Ansible también fue evolucionando y Molecule, una herramienta que [utilizo](https://tangelov.me/posts/ansible-v.html) para crear y testear roles, también ha sufrido muchos cambios.

Molecule comenzó siendo desarrollada por la comunidad, pero acabó por ser mantenida por Red Hat. Red Hat simplificó su código e hizo que fuese más estable y confiable: uno de los principales problemas que yo mismo me encontré era la facilidad con que cualquier actualización hacía que dejase de funcionar. Este tipo de inconvenientes ya no ocurren y no puedo nada más que recomendar Molecule a todo el mundo que utilice Ansible.

Red Hat no sólo ha proporcionado una mayor estabilidad a Molecule sino que también se ha esforzado en mejorar su compatibilidad con otras herramientas de la casa. Una de ellas es __Podman__, un runtime para la ejecución de contenedores que no necesita permisos de superusuario y que hace tiempo ya sustituyó a Docker en todos mis PCs. Parece cada vez más evidente que el uso de Docker se limitará a PCs de escritorio con Windows o Mac OS X, mientras en servidores pasamos a utilizar alternativas más modernas como _containerd_ o _cri-o_.

Podman no es un reemplazo absoluto de la CLI de Docker por lo que recomiendo su instalación junto a otra herramienta. __Buidah__, también creada por Red Hat, que permite crear y pushear imágenes a/desde repositorios públicos o privados. Si Podman reemplaza a _docker exec_ o _docker run_, Buildah sustituye a _docker pull_ o _docker push_.

Para instalar dichas herramientas en cualquier distribución basada en Ubuntu, podemos hacerlo con las siguientes tasks de Ansible:

```yaml
- name: Adding Podman official repository
  ansible.builtin.apt_repository:
    repo: 'deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_{{ ansible_distribution_version }}/ /'
    state: present
    update_cache: no
    filename: "devel:kubic:libcontainers:stable.list"

- name: Adding Podman official apt key
  ansible.builtin.apt_key:
    url: "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_{{ ansible_distribution_version }}/Release.key"
    state: present

- name: Installing Podman and buildah packages
  ansible.builtin.apt:
    name: 
      - podman
      - buildah
    state: present
    update_cache: yes
```

Tras probar durante meses podman y acostumbrarme a su uso, comencé a planificar la actualización de Molecule hacia sus últimas versiones. Mi primera impresión fue bastante pesimista puesto que pensé que iba a tener que rehacer todo el código, pero al final el proceso fue bastante orgánico y sencillo. Actualmente la documentación oficial es bastante mala y se encuentran muy dispersa, pero existe bastante información no oficial que podemos utilizar. Para mi caso de uso, sólo tuve que adaptar el fichero _molecule.yml_ con la siguiente configuración:

```yaml
---
dependency:
  name: galaxy
driver:
  name: podman
platforms:
  - name: centos-7
    image: centos:7
    command: /sbin/init
    tmpfs:
      - /run
      - /tmp
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
  - name: debian-stretch
    image: jrei/systemd-debian:stretch
    command: /sbin/init
    tmpfs:
      - /run
      - /tmp
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
  - name: ubuntu-bionic
    image: jrei/systemd-ubuntu:bionic
    command: /sbin/init
    tmpfs:
      - /run
      - /tmp
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
provisioner:
  name: ansible
scenario:
  name: default
  test_secuence:
    - destroy
    - create
    - converge
    - lint
    - verify
verifier:
  name: testinfra
```

Los cambios se encuentran en la parte de _platforms_ pasando de utilizar podman en lugar de docker y contenedores no privilegiados. Para mis pruebas utilizo contenedores con systemd y tan sólo tengo que añadir ciertos volúmenes y acceso a directorios temporales. El resto de la configuración no varía y prefiero seguir utilizando _testinfra_ y _pytest_ para validar los tests que escribo en Python.

Si alguien desea ver todos los cambios necesarios para portar la configuración de Molecule a las últimas versiones junto a Podman, puede hacer click [aquí](https://gitlab.com/tangelov-roles/backupninja/-/commit/030099d392cfbe0d53aaddb50970f0c12d159204).

Y esto sería todo, espero que este breve post sirva a otros para poder mantenerse actualizados y poder sacarle todo el jugo a esta gran herramienta que es Ansible. Muchas gracias y hasta la próxima.


## Documentación

* [Installing Ansible 2.1X with pip (ENG)](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#upgrading-from-2-9-or-earlier-to-2-10)

* [The Future of Ansible Content Delivery (ENG)](https://www.ansible.com/blog/the-future-of-ansible-content-delivery)

* [Ansible 3.0.0 QA (ENG)](https://www.ansible.com/blog/ansible-3.0.0-qa)

* [Ansible Collections in Github (ENG)](https://github.com/ansible-collections)

* [Documentación oficial de Podman (ENG)](http://docs.podman.io/en/latest/)

* [Getting started with Buildah (ENG)](https://developers.redhat.com/blog/2021/01/11/getting-started-with-buildah)

* [Documentación oficial de Testinfra (ENG)](https://testinfra.readthedocs.io/en/latest/)

Revisado a 11/07/2021
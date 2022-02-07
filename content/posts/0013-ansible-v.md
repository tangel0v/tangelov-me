---
title: "Ansible (V): testeando roles con Molecule"
slug: ansible-v
authors:
  - tangelov
date: 2018-09-02T07:00:00+02:00
tags:  ["ansible", "python"]
categories: ["devops"]
draft: false
---

En el post [anterior](https://tangelov.me/posts/ansible-iv.html) sobre Ansible ya teníamos un rol plenamente funcional, pero siempre podemos mejorarlo un poco más.

Imaginemos que realizamos cambios en nuestro rol y queremos probarlos a medida que seguimos desarrollándolo y que en una de las pruebas omitimos sin querer algun test y al aplicarno en nuestros servidores rompemos algo. Todo el desarrollo realizado anteriormente podría provocar pérdidas de datos o de servicio debido a un error humano.

¿Cómo podemos evitarlo? Podemos añadir a nuestro rol, [Molecule](https://molecule.readthedocs.io/en/latest/).

> __Nota del autor__: Molecule ha sido completamente reescrito en los últimos tiempos y el contenido de este post no es válido en las últimas versiones de la herramienta. Por lo tanto, este artículo queda con carácter consultivo y quien desee ver información actualizada, puede hacerlo en [éste otro](https://tangelov.me/posts/ansible-vi.html).

<!--more-->

## Introducción
Molecule es un programa escrito en python que nos permite probar cada cambio que realicemos en nuestro rol contra una instancia que se crea y se destruye para cada ocasión. De esta forma podremos probar cada cambio que realicemos en nuestros roles de Ansible y asegurarnos cual será su comportamiento cuando los despleguemos en los servidores reales, evitando molestias y sustos.

Por defecto, Molecule utiliza contenedores para levantar entornos contra los que hacer pruebas por lo que deberemos instalar el demonio de Docker, pero se puede utilizar otras tecnologías de virtualización como KVM o proveedores de Cloud Pública como AWS o Azure.

Si realizamos ```molecule --help``` veremos todos los comandos que podremos utilizar. No vamos a citarlos todos pero si los más importantes:

* _init_ : Nos creará la estructura básica de un rol y preparará los ficheros usados por Molecule para poder generar de forma automática las máquinas virtuales o los contenedores en los que realizar las pruebas.

* _create_: Utiliza el _provisioner_ (el encargado de generar la instancia) para generar una plantilla y una instancia compatible con el uso de Ansible.

* _converge_: Realizará una serie de pasos que podemos definir para añadir características propias a nuestras plantillas. Por ejemplo, si necesitamos que nuestro rol utilice una base de datos particular, podemos crearla en este paso.

* _test_: Realizará paso a paso todos los tests posibles: desde sintaxis hasta los tests que programemos con pytest o testinfra que añadirán más comprobaciones a todo el proceso.

* _destroy_: Destruye las instancias creadas anteriormente y permite empezar de cero todo el proceso. 

*****

## Añadimos Molecule a nuestro rol
A día de hoy no podemos añadir Molecule a un rol ya creado previamente de forma automática. Pero se puede hacer un pequeño truco, que consiste en renombrar temporalmente nuestro rol, crearlo con molecule y luego copiar el contenido original a donde se encuentra el rol. Por ejemplo:

```bash
mv backupninja backupninja_old
molecule init role backupninja

cp -R backupninja_old/* backupninja/
```

Ahora dentro de la carpeta de backupninja tendremos una nueva carpeta que se llama molecule. Vamos a inspeccionarla:

```bash
ls -laRt
.:
total 12
drwxr-xr-x 11 tangelov tangelov 4096 feb 28 10:40 ..
drwxr-xr-x  4 tangelov tangelov 4096 feb 28 10:40 default
drwxr-xr-x  3 tangelov tangelov 4096 feb 27 15:04 .

./default:
total 36
drwxr-xr-x 4 tangelov tangelov 4096 feb 28 10:40 .
-rw-rw-r-- 1 tangelov tangelov 3195 feb 28 10:20 prepare.yml
-rw-rw-r-- 1 tangelov tangelov  687 feb 27 15:06 molecule.yml
drwxr-xr-x 3 tangelov tangelov 4096 feb 27 15:04 ..
drwxr-xr-x 3 tangelov tangelov 4096 feb 27 13:42 tests
-rw-r--r-- 1 tangelov tangelov  614 ene 11  2020 converge.yml
drwxr-xr-x 2 tangelov tangelov 4096 ene  7  2020 files
-rw-r--r-- 1 tangelov tangelov 1153 ene  7  2020 Dockerfile.j2
-rw-r--r-- 1 tangelov tangelov  369 ene  7  2020 INSTALL.rst

./default/tests:
total 16
drwxr-xr-x 4 tangelov tangelov 4096 feb 28 10:40 ..
drwxr-xr-x 2 tangelov tangelov 4096 feb 27 15:03 __pycache__
drwxr-xr-x 3 tangelov tangelov 4096 feb 27 13:42 .
-rw-r--r-- 1 tangelov tangelov  523 ene  7  2020 test_default.py
```

## Primeros pasos con Molecule
Ahora nos movemos a la carpeta molecule/default dentro la carpeta de nuestro rol. Vamos a centrarnos en tres ficheros:

* _molecule.yml_ : es el fichero principal para configurar cómo se va a comporar molecule en nuestro rol.

* _prepare.yml_: es el fichero principal encargado de ejecutar los pasos que preparan las instancias para poder ejecutar luego nuestros roles dentro de molecule.

* _converge.yml_: es el fichero encargado de ejecutar el rol dentro de molecule.

* _Dockerfile.j2_: Por defecto, Molecule utiliza Docker para crear las instancias, salvo que indiquemos que utilice otro _provider_ siempre tendremos este fichero y es el encargado de hacer que nuestro contenedor sea compatible con Ansible.

Simplemente si hacemos ```molecule create``` veremos algo similar a esto:

```bash
--> Validating schema ~/backupninja/molecule/default/molecule.yml.
Validation completed successfully.
--> Test matrix
    
└── default
    ├── create
    └── prepare
    
--> Scenario: 'default'
--> Action: 'create'
    
    PLAY [Create] ******************************************************************
    
    TASK [Log into a Docker registry] **********************************************
    skipping: [localhost] => (item=None) 
    skipping: [localhost]
    
    TASK [Create Dockerfiles from image names] *************************************
    changed: [localhost] => (item=None)
    changed: [localhost]
    
    TASK [Discover local Docker images] ********************************************
    ok: [localhost] => (item=None)
    ok: [localhost]
    
    TASK [Build an Ansible compatible image] ***************************************
    changed: [localhost] => (item=None)
    changed: [localhost]
    
    TASK [Create docker network(s)] ************************************************
    skipping: [localhost]
    
    TASK [Create molecule instance(s)] *********************************************
    changed: [localhost] => (item=None)
    changed: [localhost]
    
    TASK [Wait for instance(s) creation to complete] *******************************
    changed: [localhost] => (item=None)
    changed: [localhost]
    
    PLAY RECAP *********************************************************************
    localhost                  : ok=5    changed=4    unreachable=0    failed=0
```

Vamos a editar el fichero molecule.yml en _molecule/default_ para generar dos contenedores uno con Debian y otro con Centos sobre los que probar nuestro rol. Eso se realiza añadiendo diferentes imágenes en la zona de _platforms_, quedando así el fichero:

```yaml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: debian
    image: jrei/systemd-debian
    command: /lib/systemd/systemd
    privileged: true
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
  - name: ubuntu
    image: jrei/systemd-ubuntu
    command: /lib/systemd/systemd
    privileged: true
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
  - name: centos
    image: centos/systemd
    command: /sbin/init
    privileged: true
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

Si ahora ejecutamos _molecule create_ y hacemos _docker ps_ podremos ver nuestros contenedores corriendo:

```bash
CONTAINER ID        IMAGE                                COMMAND                  CREATED             STATUS              PORTS               NAMES
f2532c299664        molecule_local/centos/systemd        "/sbin/init"             2 minutes ago       Up About a minute                       centos
4656b5096126        molecule_local/jrei/systemd-ubuntu   "/lib/systemd/systemd"   2 minutes ago       Up About a minute                       ubuntu
b7473fafb19a        molecule_local/jrei/systemd-debian   "/lib/systemd/systemd"   2 minutes ago       Up About a minute                       debian
```

Hemos usado contenedores privilegiados para correr los test y controlar _systemd_ al estilo de una máquina virtual clásica.


## Configuraciones extra
Nuestro siguiente paso es realizar ```molecule converge```. Este paso desplegará nuestro rol en los contenedores que hemos creado y aplicará todas las tareas que hemos creado anteriormente. 

Para no hacer el post demasiado largo, vamos a suponer que el despliegue de nuestro rol no falla. Sin embargo, antes de ejecutar _converge_ necesitamos crear un entorno que simule lo que tenemos en nuestro servidor creando una ruta con ficheros sueltos en /var/www y una base de datos corriendo en ella.

Ahora creamos un fichero llamado ~/backupninja/molecule/default/prepare.yml. Este fichero contiene los pasos previos que utiliza molecule para dejar el entorno preparado para probar nuestros roles y vamos a añadir algunas acciones para simular nuestros servidores.

Como el fichero es muy largo, lo referencio [aquí](https://gitlab.com/tangelov-roles/backupninja/blob/fb19760f19b69f5bc66c1360def90784de633cda/molecule/default/prepare.yml).

Al ejecutar ```molecule converge```primero se ejecutará nuestro _prepare.yml_ y después se ejecutará _playbook.yml_ que lanzará nuestro rol propiamente dicho.

Si ahora nos metemos dentro de las instancias con _molecule login --host $nombre_ podremos ver que nuestros backups se han creado, pero lo ideal es que Molecule lo compruebe por nosotros, así que vamos a editar el fichero _backupninja/molecule/default/tests/test_default.py_ y a añadir el siguiente código.:

```python
import os
import testinfra.utils.ansible_runner
import datetime

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_backupninja_dump_exists(host):
    """Checking if the file generated in default test last step exists"""
    with host.sudo():
        bckdate = datetime.datetime.utcnow().strftime("%Y.%m.%d")
        bckpath = '/def_test/' + 'full-test' + '-' + bckdate + '.tgz'

        f = host.file(bckpath)
        assert f.exists
```

Estos test, escritos en Python y utilizando _testinfra_, nos permiten realizar ciertas comprobaciones de forma automática. Este código, simplemente comprueba si se ha generado nuestro backup al realizar _molecule test_, con el formato que hemos aplicado en el script de backupninja.

Aquí podremos ver el proceso entero utilizando _molecule test_ (el gif dura cinco minutos así que... un poco de paciencia :D ):

![molecule-gif](https://storage.googleapis.com/tangelov-data/images/0013-00.gif)

El gif muestra como se realiza la creación de las instancias, el despliegue del entorno de pruebas y nuestro rol en él y finalmente si éste es idempotente y si el test automático de Molecule ha pasado o no.

> En el pasado introduje un error al crear el fichero _playbook.yml_ en lugar de _prepare.yml_. Esto causaba problemas de idempotencia en los tests de molecule pero ya está solucionado.

Con esto, terminamos el post. En el siguiente añadiremos algo más de complejidad a los tests y explicaremos más en profundidad los pasos que realiza molecule.

Un saludo y espero que os haya resultado interesante.


## Documentación

* [Documentación oficial de molecule (ENG)](https://molecule.readthedocs.io/en/latest/)

* [Driver de Docker en Molecule (ENG)](https://molecule.readthedocs.io/en/latest/configuration.html#docker)

* [Debian con Systemd en Docker](https://hub.docker.com/r/jrei/systemd-debian/) y [Centos con Systemd en Docker](https://hub.docker.com/r/centos/systemd/)

* [Documentación oficial de Testinfra (ENG)](https://testinfra.readthedocs.io/en/latest/)

Revisado a 01/03/2022

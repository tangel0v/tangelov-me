---
title: "Ansible (I): primeros pasos"
slug: ansible-i
authors:
  - tangelov
date: 2018-02-24T18:00:00+02:00
tags:  ["ansible", "python"]
categories: ["devops"]
draft: false
---

Desde que descubrí Ansible, mi vida es un poco más feliz. Pero... ¿Qué es y para que sirve?

Ansible es una plataforma que permite realizar de forma automatizada aprovisión, gestión, configuración y despliegue de aplicativos basándose en una serie de principios:

* Debe ser segura, consistente y _mínima_ (se deben evitar todas las dependencias posibles: solo requiere de SSH y Python para funcionar). Esto le permite funcionar tanto en infraestructuras basadas en x86 como en ARM (como una Raspberry Pi).

* Debe ser __confiable__: se busca que las acciones ejecutadas por Ansible sean idempotentes: es decir, que podamos aplicar una acción muchas veces sin que cambie el resultado tras la primera ejecución.

<!--more-->

## Instalación y estructura
Ansible consta, al menos, de un nodo que lanza las órdenes y de un nodo que las recibe y las ejecuta (los cuales pueden ser el mismo).

El primer paso es instalar Ansible. Tras instalar las dependencias (python y openssh), podremos instalarlo cn el siguiente comando:

```bash
# Se recomienda instalar Ansible con Pip
pip3 install ansible --user
```

Una vez instalado, vamos a ver que nos ha generado:

```bash
[tangelov@portatil ansible] $ tree
.
├── ansible.cfg
├── hosts
└── roles
```

Son dos ficheros y un directorio:

* _ansible.cfg_ es el fichero donde se almacena por defecto toda la configuración de ansible. Ahí podemos ver cual es el fichero que contiene los hosts a los que puede conectarse y cómo lo va a hacer.

* _hosts_ es la lista por defecto de hosts donde Ansible puede conectarse.

* _roles_: es una carpeta extra donde por defecto ansible busca _roles_ que podremos usar en nuestros _playbooks_.

### Glosario
¿Roles, playbooks? Antes de seguir, mejor explico un poco la terminología usada por Ansible:

* Un módulo es un _script_ que permite realizar cambios en una máquina de manera idempotente (al menos en teoría)

* Una _task_ es una tarea: una acción o acciones que realizamos en una serie de hosts, utilizando módulos, etc.

* Un rol es una lista de tareas que hemos generado y que conforman entre todas una acción única. Por ejemplo podemos hacer un rol para instalar Wordpress ejecutando diferentes tareas, paso a paso. Un rol puede contener otros roles.

* Un playbook es un script de Ansible escrito en yaml que nos permite ejecutar una serie de tareas y/o roles según nuestro criterio. También deberían ser idempotentes.

* Inventario: un inventario es una lista de hosts a los que Ansible puede conectarse, agrupados o no. Podemos tener más de uno.

## Configuración
En principio, Ansible tan sólo necesita tener acceso a través de SSH a las máquinas a la que nos vayamos a conectar, ya sea copiando una llave SSH o usando la contraseña de un usuario en concreto. Para indicarle a que hosts nos vamos a conectar, debemos utilizar un fichero de _inventario_. Por defecto se usa el fichero _/etc/ansible/hosts_.

Para explicar cómo funciona un inventario, vamos a representar una posible infraestructura de una página web formada por dos frontales, tres nodos de bases de datos como _backend_, un servidor de LDAP para gestionar la autenticación y una conexión contra la máquina en local desde donde se lanza Ansible. 

```bash
[local]
localhost   ansible_connection=local

[frontales]
frontal01.tangelov.me   ansible_connection=ssh    ansible_user=userweb
frontal02.tangelov.me   ansible_connection=ssh    ansible_user=userweb

[databases]
db01.tangelov.me    ansible_port=50022   ansible_user=userdb
db02.tangelov.me    ansible_port=50022   ansible_user=userdb
db03.tangelov.me    ansible_port=50022   ansible_user=userdb

[autenticacion]
ldap.tangelov.me    ansible_host=192.168.1.10
```

Como vemos, el archivo está dividido en cuatro grupos diferentes: local, frontales, databases y autenticacion y éstos a su vez pueden estar formados por uno o más hosts:

* local: se corresponde con el grupo _local_, que se corresponde a la máquina donde tenemos instalado Ansible y usa un método de conexión diferente a SSH (existen más métodos de conexión, como Docker, etc.)

* frontales: se corresponden con dos servidores cuyo nombre DNS son frontal0X.tangelov.me a las que Ansible se conecta utilizando el usuario _userweb_, utilizando el puerto 22 (el puerto usado por defecto para SSH).

* databases: se corresponde con tres servidores cuyo nombre DNS es db0X.tangelov.me. Debido a que no usan el puerto por defecto, debemos indicárselo así como el usuario, que ahora es _userdb_

* autenticacion: se corresponde con el nombre ldap.tangelov.me y a su vez con el host de IP 192.168.1.10. Se puede pasar la dirección IP cuando la resolución DNS no se corresponda. En el resto de valores se tomarán los valores por defecto (conexión por SSH, puerto 22 y el usuario que estamos utilizando)

## Primeros pasos
Para realizar un par de primeras pruebas, vamos a utilizar la conexión local, que ya hemos generado. Para probar la conexión, vamos a utilizar y explicar el siguiente comando ``ansible local -m ping``

Estaríamos tirando el módulo _ping_ (para probar la conexión) contra el grupo _local_. En caso de ser correcta, la ejecucion debería devolver algo similar a esto:
```bash
[tangelov@portatil ~] $ ansible local -m ping
localhost | SUCCESS => {
    "changed": false, 
    "ping": "pong"
}
```

Existen una gran cantidad de módulos: nos permiten modificar ficheros, añadir usuarios, instalar o desinstalar paquetes, controlar sistemas Windows, controlar repositorios, añadir o modificar características de nuestros sistemas (SELinux por ejemplo), etc, etc. Las posibilidades son casi infinitas.

Ahora vamos a coger el comando antes ejecutado y lo vamos a convertir en un pequeño playbook. Crearíamos el fichero ansible-test.yaml tal que así:

Sería tal que así:
```yaml
---
- hosts: local
  tasks:
  - name: Testing connectivity
    ping:
```

En este fichero hemos indicado que host va a ser el encargado de ejecutar el playbook y hemos definido una tarea que símplemente lanza el módulo de _ping_. Lo ejecutamos así ``ansible-playbook ansible-test.yaml`` y si todo sale bien deberíamos recibir lo siguiente por pantalla.

```bash
[tangelov@portatil ~] $ ansible-playbook ansible-test.yaml 

PLAY [local] **************************************************************************************************************************

TASK [Gathering Facts] ****************************************************************************************************************
ok: [localhost]

TASK [Testing connectivity] ***********************************************************************************************************
ok: [localhost]

PLAY RECAP ****************************************************************************************************************************
localhost                  : ok=2    changed=0    unreachable=0    failed=0  
```

Profundizaremos más adelante sobre el tema: organización interna, gestión de roles y muchas cosas más.


## Documentación

* [Página web oficial de Ansible (ENG)](https://www.ansible.com/)

* [Blog oficial de Ansible (ENG)](https://www.ansible.com/blog)

* [Ansible (ENG)](https://en.wikipedia.org/wiki/Ansible_(software))

* [Lista de módulos de Ansible (ENG)](http://docs.ansible.com/ansible/latest/list_of_all_modules.html)

* [Inventarios en Ansible (ENG)](http://docs.ansible.com/ansible/latest/intro_inventory.html)

Revisado a 01/02/2020

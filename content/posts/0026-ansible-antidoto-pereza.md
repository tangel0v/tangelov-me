---
title: "Ansible: el gran remedio a la pereza"
slug: ansible-antidoto-pereza
authors:
  - tangelov
date: 2020-01-16T18:00:00+02:00
tags:  ["ansible"]
categories: ["devops"]
draft: false
---

Como comenté en el post anterior, uno de los problemas que tuve el año pasado estuvo relacionado con mi portátil personal: llegado un momento el GRUB de mi PC se corrompió y no hubo manera de arreglarlo. Intenté reinstalarlo, arreglar los ficheros de GRUB que habían petado, hacer un chroot desde un CD live y hacer una reparación manual desde ahí, paso a paso.

Tras probar durante unas horas, decidí que lo mejor era reinstalar de 0 puesto que sólo había perdido tiempo y no datos. Y aunque siempre hago un seguimiento de qué tengo instalado, ahí fue cuando me di cuenta de la pereza que me daba reconfigurarlo todo. Llegados a este punto pensé... ¿por qué no utilizar mis conocimientos de automatizaciones para evitar _perezas futuras_?

<!--more-->

## Pasos previos
Para la configuración de mi escritorio, pensé rápidamente en Ansible y tras una [rápida búsqueda](https://www.google.com/search?&channel=fs&q=gnome+ansible&ie=utf-8&oe=utf-8) por Internet vi que no era el único que había tenido el mismo problema. En principio yo tenía las siguientes necesidades:

* Utilizo bastantes herramientas en formato CLI cuya configuración es descargar, descomprimir y ejecutar. Utilizo muchos alias para la gestión de las mismas y personalizo mi prompt. Sabía que no iba a tener problemas con esta parte.

* Utilizo Gnome Shell desde hace años. Siempre me ha gustado GTK y las aplicaciones construidas con sus librerías. También utilizo herramientas empaquetadas en formato snap y flatpak. Era con estos puntos con los que tenía más dudas: no sabía si Ansible soportaba sus configuraciones puesto que aunque todo se puede hacer con módulos _shell_ o _command_, prefería que fuese un poco más idempotente.

## Herramientas
Al final tras unas pocas horas de trabajo desglosé gran parte de las necesidades y generé un playbook que podía usar para configurar mi portátil (aunque todavía no hace todo lo que quiero, si hace lo más tedioso). En general, en la fecha de publicación de este post (16-01-2020) su estado actual es el siguiente:

1. Instala las utilidades básicas que necesito y sus dependencias (git, vim, tmux, etc)

2. Genera una estructura de carpetas que siempre utilizo para introducir las utilidades que uso (como _kubectl_ por ejemplo) y almacenar los desarrollos personales que hago.

3. Instala y configura _zsh_ con todo lo que necesito.

4. Configura mi escritorio: instala los iconos, temas y extensiones de Gnome Shell que suelo utilizar.

5. Instala múltiples aplicaciones: a través de _snap_, de _flatpak_, paquetes del sistema, herramientas en binario, CLIs que utilizo y otros.

6. Instala y habilita mi sistema de backups.

Pese a no estar completo al 100%, es bastante robusto y ya me quita de gran parte del trabajo. La idea es irlo manteniendo y añadiendo todas las funcionalidades que me faltan para que cubra todas mis necesidades en un plazo de 1-2 meses. Una de ellas por ejemplo, es definir una variable con el nombre de un backup y que él mismo se encargue de restaurarlo.


### Modularidad: roles y tags
La primera versión que tuve era funcional, pero poco usable puesto que tenía todas sus tareas introducidas en un único fichero, con las variables justas y necesarias. De esta forma, cada vez que introducía un cambio tenía que ejecutar el playbook entero. También organicé de forma física el playbook original, agrupando las tareas que tenían cierta relación entre si en distintos ficheros y quedando en este estado:

```bash
├── launcher.sh
├── main.yml
├── vars.yml
├── vault.yml
├── requirements.yml
├── README.md
└── tasks
    ├── apps
    │   ├── flatpak.yml
    │   └── snap.yml
    ├── backups.yml
    ├── common.yml
    ├── devops-cloud
    │   ├── cloud.yml
    │   ├── hashicorp.yml
    │   ├── requirements.txt
    │   └── virtualbox.yml
    ├── gnome-conf.yml
    └── others.yml
```

Tras darle orden y puesto que voy a seguir ampliando el sistema, comencé a _modularizar_ su contenido, siendo la manera más sencilla de hacerlo con el uso de _tags_ de Ansible.

Los tags me permiten agrupar por tipo ciertas tareas y aplicar las configuraciones sólo referentes a ese tag. Así si actualizo la CLI de AWS porque ha salido una versión nueva, tan sólo tengo que ejecutar el playbook con la tag de _cloud_ y la configuración se aplicará de una forma mucho más ágil. Por ejemplo:

```yaml
- name: Installing Cloud provider CLIs
    tags: cloud
    block:
      - name: Installing Cloud resources
        import_tasks: tasks/devops-cloud/cloud.yml
```

A medida que avancé en el desarrollo vi que algunas partes podían funcionar de manera atómica y comencé a migrar ciertas partes a roles. Algunas partes de mi código fueron sustituidas por roles públicos con algunas tareas extra, pero también [puse al día](https://gitlab.com/tangelov-roles/backupninja) mi rol de [backupninja](https://tangelov.me/posts/ansible-iv.html). Ahora existen diferentes versiones del rol y soporta entre otras cosas cifrado de los backups con GPG y puedes aplicarle un sistema de retención en función de lo que necesites.


### Generalización
Empecé este proyecto casi como un berrinche provocado por tener que volver a _reinstalarlo todo_ tras un desastre, así que no veía la necesidades de publicar el código. Cuando comencé a modularizar el sistema, vi que podía usar el sistema de backups de manera unificada tanto en mi PC como en otros servidores y que mantenerlo público era una manera de evitar la dejadez y ponerme las pilas con su documentación, con su calidad y con la seguridad.

Su [código](https://gitlab.com/tangelov/configuration) está disponible en Gitlab y todo el que quiera puede echar un vistazo, usarlo o mejorarlo. Para comenzar a utilizarlo tan sólo tenemos que clonar el repositorio, crear un inventario compatible (se explica cómo hacerlo en la documentación con ejemplos) y que el host a configurar esté basado en sistemas Ubuntu.

He intentado que se cumplan todas las buenas prácticas que he podido y ya lo utilizo en todos mis servidores y ordenadores. También he generado algunos scripts extra en bash para permitirme cargar otras configuraciones o realizar instalaciones preeliminares.

Si quisiese actualizar mi sistema de backup, tan sólo tendría que ejecutar el siguiente comando:

```bash
ansible-playbook -i inventory main.yml --tags backups --ask-become-pass --ask-vault-pass --limit=localhost
```

Espero continuar perfeccionando el sistema y convertir cada vez más partes del playbook en roles que puedan ser aprovechados de manera independiente (la instalación de las herramientas de Hashicorp es muy fácil de implementar).

Espero que sea de utilidad y muchas gracias!


## Documentación

* Repositorio del sistema de [configuración](https://gitlab.com/tangelov/configuration)

* Rol de [Backupninja](https://gitlab.com/tangelov-roles/backupninja)


Revisado a 01/03/2021

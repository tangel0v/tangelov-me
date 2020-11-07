---
title: "Mi nube privada: Nextcloud, ARM y un poco de Cloud"
slug: mi-nube-privada
authors:
  - tangelov
date: 2019-01-03T23:00:00+02:00
tags:  ["nextcloud", "backup"]
categories: ["cloud"]
draft: false
---

En el mundo en el que vivimos, la nube se está extendiendo gracias a la proliferación de servicios integrados, ya sea en móviles, en electrodomésticos. El uso de los servicios ya gestionados por terceros, listos para utilizar, es algo generalizado: los de Google (Google Docs, Google Drive o GMail entre otros) son usados por casi todos los usuarios de Android, pero éstos no son los únicos y tenemos otros como [Zoho](https://www.zoho.com/), [Office 365](https://products.office.com/es-ES/compare-all-microsoft-office-products) o [Quip](https://quip.com/intl/es/) entre otros.

Sin embargo también existen alternativas que ofrecen experiencias más o menos equivalentes y que podemos instalar y gestionar nosotros. Ya hemos hablado en el pasado de [Nextcloud](https://tangelov.me/posts/nube-privada-nextcloud.html) pero no son los únicos: [Cozy](https://cozy.io/es/) (Parecido a Google Drive), [Turtl](https://turtlapp.com/) (Una alternativa a Evernote) u otros...

Siempre me ha gustado montar los servicios que utilizo, por aprender y valorar lo que me ofrecen y gracias a la proliferación de placas como la Raspberry Pi, me he montado un sistema propio combinando algunos servicios antes citados.

<!--more-->

## Introducción
Cuando estudiaba en la universidad los únicos servicios que utilizaba eran Dropbox para sincronizar ficheros entre mis diferentes PCs y tener una copia fuera de mi casa (fundamentalmente apuntes) y una cuenta de Google ligada a mi móvil Android (para el correo y evitar que mis contactos se perdieran).

Sin embargo, aunque siempre quise tener un servidorcillo casero, nunca me decidía ni sobre que servicios tenía que tener ni sobre que hardware iba a ser. 

Todo eso cambió cuando empezó a mejorar Owncloud en torno a finales del 2013 y tome la decisión de que quería uno así para mi.

## Hardware
Tras un par de pruebas satisfactorias con máquinas virtuales, me puse a investigar sobre el hardware que podía usar y rebuscando encontré un blog que me ayudó mucho [raspberryparatorpes.net](https://raspberryparatorpes.net/).

Ya había descartado el uso de placas ATX debido a su _alto_ consumo energético y me había empezado a interesar por las placas de desarrollo, especialmente por las Raspberry Pi. Aunque me gustaba su precio, no me convencían algunos de los puntos de dichas placas: su velocidad de red era baja y compartían el bus con los USBs, por lo que si enchufaba un disco duro (ya tenía dos que había sacado de portátiles rotos) sería un gran cuello de botella.

Así que decidí esperar hasta que saliera algo acorde a mis necesidades y pocos meses después llegó una placa hecha casi a medida: la Banana Pi M1. Con más potencia de procesamiento, un puerto Gigabit Ethernet y un SATA2 al que enchufarle un disco duro, era todo lo que necesitaba. Sus especificaciones completas están [aquí](http://www.banana-pi.org/m1.html).


## Servicios
Aunque primero la estructura de servicios fue variando, con el paso del tiempo aprendí a utilizar servicios estables, que me dieran poco trabajo y un gran provecho, quedando así estructurada "mi nube":

* El sistema operativo utilizado en la placa es una versión de Debian para placas de desarrolladores llamado Armbian. Es estable y duro como una roca.

* Necesitaba un sistema de almacenamiento de ficheros que tuviese capacidad de sincronización, cliente web, clientes para móviles y al menos soportara calendarios y contactos. Actualmente uso Nextcloud con algunos plugins.

* Extras: gestión de la publicidad de mis dispositivos y posibles ampliaciones.

Estoy en proceso de publicar roles y playbooks de Ansible para que todo el sistema sea replicable y personalizable por terceros.


#### Nextcloud
La base de todo el sistema es mi instancia de Nextcloud que está montada sobre un disco duro cifrado y se sirve gracias a Letencrypt (para generar certificados válidos de forma automática), a Nginx (para publicar la página) y a PHP en versiones superiores a la 7.1. Además de lo habitual (ficheros, contactos, calendarios y tareas) utilizo un plugin que me aporta un sistema básico de Kanban que utilizo para desarrollar mis proyectos personales.

#### Pihole
Antiguamente utilizaba bloqueadores de publicidad en los navegadores puesto que a veces algunas páginas web hacen un auténtico abuso de ésta, pero recientemente he empezado a tener problemas debido a que muchas webs detectan que tienes instalado un bloqueador, ya sea Adblock Plus o Ublock y comencé a utilizar [PiHole](https://pi-hole.net/) recientemente. Los resultados son inmejorables y afectan también a móviles y a aparatos inteligentes.

Instalarlo es tan sencillo como ejecutar el comando: ```curl -sSL https://install.pi-hole.net | bash``` y contestar las preguntas que el script nos haga.

## Backups y seguridad
Una de las mayores limitaciones que tiene la autogestión de servicios es que tu no tienes la capacidad que tiene una gran empresa para ofrecer redundancia de datos o tolerancia a fallos en ámbitos geográficos, algo que todos los proveedores de nube ofrecen y por ello debes apostar por otras opciones si quieres mantener unos costes bajos. En mi caso, he apostado por no tener alta disponibilidad y mandar mis backups a la nube lejos de mi casa. Así siempre tendré copias de mis datos en algúne ofrecen y por ello debes apostar por otras opciones si quieres mantener unos costes bajos. En mi caso, he apostado por no tener alta disponibilidad y mandar mis backups a la nube.

Para conseguirlo utilizo dos herramientas: _backupninja_ y _rclone_.

* __backupninja__: Es un sistema que ya he comentado en el blog y que utilizo en mis servidores para hacer backups completos. En este caso realizo backups completos y para agilizar los procesos de recuperación en el caso de ser necesario. Todo ello cifrado con GPG.

* __rclone__: Es un programa realizado en Go que imita el comportamiento de rsync pero contra sistemas de almacenamiento en la nube. Los backups se almacenan aquí y en caso de ser necesario se podrían usar para restaurar el sistema entero. La cantidad de sistemas que soporta es enorme y en mi caso utilizo los tier gratis de diversos proveedores de nube para subir mis backups periódicamente y evitar que un desastre pudiera hacerme perder los datos. Por ejemplo, MEGA ofrece 50 GB que podríamos utilizar para almacenar hasta un histórico de backups sin problemas.


![backups](https://storage.googleapis.com/tangelov-data/images/0020-00.png)


## Costes del sistema
Estoy muy contento con los costes del sistema en total:

* La Banana Pi me costó entre 30 y 35 euros con los gastos de envío.
* Los gastos extra asociados a ella fueron sólo unos 10 euros en la carcasa (impresa con una impresora 3D) y otro tanto en la tarjeta SD. El disco duro fue reaprovechado.
* El coste energético es similar al de una Raspberry Pi, un poco superior debido al disco duro pero es prácticamente despreciable al muy inferior al de una bombilla de bajo consumo (Unos siete euros anuales si la placa estuviese al 100% de consumo todo el tiempo).


Y nada, recomiendo a todo el mundo que le guste el cacharreo que se monte uno, la verdad es que es muy divertido. Espero que os haya gustado, un saludo a todos.

## Documentación

* [El cuello de botella de la Raspberry Pi](https://raspberryparatorpes.net/dudas/el-cuello-de-botella-de-la-raspberry-pi/)

* [Armbian para Banana Pi M1 (ENG)](https://www.armbian.com/bananapi/)

* [Instalar PiHole con Nginx (ENG)](https://docs.pi-hole.net/guides/nginx-configuration/)

* [Instalación de Rclone (ENG)](https://rclone.org/downloads/)

Revisado a 01/02/2020

---
title: "Aplicaciones para DevOps (I)"
slug: devops-apps
authors:
  - tangelov
date: 2018-10-14T07:00:00+02:00
tags:  ["apps"]
categories: ["devops"]
draft: false
---

Hace años, era realmente difícil encontrar aplicaciones que funcionaran para los principales s
istemas operativos, quedándose Linux frecuentemente al margen. Sin embargo, de unos años para
aquí, con el crecimiento de la nube y de las aplicaciones web esto parece estar cambiando. Val
ve con su cliente _Steam_ o Microsoft con su IDE _Visual Studio Code_ son dos ejemplos de esta
 tendencia.

El auge de tecnologías web ha permitido que aparezcan frameworks que facilitan la creación de
aplicaciones de escritorio multiplataforma. El más conocido de todos ellos es [Electron](https://en.wikipedia.org/wiki/Electron_(software_framework)).

<!--more-->

## Electron
Electron es un framework de código abierto desarrollado por Github que nos permite crear aplicaciones web utilizando herramientas web. Utiliza [NodeJS](https://nodejs.org/es/) para el backend y el motor de [Chromium](https://www.chromium.org/Home) como Frontend. Por otro lado, también suelen ser aplicaciones que _pesan_ bastante, por lo que debemos tener un PC decente si vamos a usar unas cuantas abiertas.

Existen muchas aplicaciones construidas bajo electron. Aparte de las antes citadas, son también muy conocidas:

* Spotify: El mayor servicio de música en streaming en el mundo lo utiliza en su aplicación.

* Whatsapp y Signal: Son dos servicios de mensajería para móviles y tienen su aplicación de escritorio construida en Electron.

* Discord y Twitch: Son dos servicios muy usados para _gamers_ cuyo cliente para escritorio utiliza Electron como base.

* El cliente de escritorio del servicio de blogging más usado del mundo, Wordpress. 

Si tenemos mucha curiosidad, podemos ver todas las aplicaciones construidas con electron [aquí](https://electronjs.org/apps)


## Aplicaciones para DevOps
Gracias a esta explosión de aplicaciones, tenemos muchas aplicaciones que podemos usar para metodologías devops y para trabajo en equipo. Estuve buscando algunas que pudieran serme útiles, con tres criterios (que estuvieran actualizadas, que no fueran de pago o al menos tuvieran una versión sin coste y que tuvieran una cierta progresión) y esto es lo que encontré:

* __Keeweb__: La gestión de secretos siempre suele ser algo peliagudo. Aunque existen muchos servicios que proporcionan este tipo de gestiones (como LastPass), prefiero utilizar un servicio controlado por mi en lugar de uno gestionado. Keeweb, nos permite crear un fichero cifrado que podemos sincronizar con Dropbox, Onedrive, Google Drive o nuestro propio servidor, revisar si nuestras credenciales han sido comprometidas y además es totalmente compatible con [Keepass](https://keepass.info/). 

* __Chronos Timetracker__: Es un cliente de escritorio para [Jira](https://es.atlassian.com/software/jira), el _"bug tracker"_ ágil de Atlassian, escrito en Electron.

* __Rambox__: Si utilizamos muchos servicios en la nube podemos utilizar esta aplicación para juntarlos todos en una misma interfaz. Tiene una versión de pago que añade más servicios. También podemos usar [_Station_](https://getstation.com/). Existen multitud de agregadores de servicios web realizados en Electron.

* __Insomnia__ o __Postman__: Son clientes para realizar peticiones REST potentísimos y que podemos utilizar para desarrollar y probar cualquier tipo de API REST. Si por ejemplo estamos realizando alguna integración contra la API de Azure o cualquier otra API, podemos ver que nos responde con _Insomnia_.

* __SQLelectron__: Es un cliente SQL que nos permite conectarnos a multitud de bases de datos relacionales (MySQL, PostgreSQL, SQL Server, SQLite y Cassandra). Tiene una versión para terminal. Otras bases de datos no relacionales, tienen un cliente propio, también escrito en Electron, como MongoDB.

* __Dockstation__: Dentro del mundo DevOps, se utilizan mucho contenedores y microservicios y Dockstation es un cliente de escritorio que nos permite gestionar nuestros proyectos creados sobre contenedores y que añade monitorizaciones y opciones extra.

* __Vagrant Manager__: Añade una opción en nuestra barra de estado que nos permite controlar nuestras máquinas virtuales gestionadas con Vagrant de una forma centralizada. (Ya hablaré de Vagrant en post futuros).

* __Shiba__: Markdown es un lenguaje muy utilizado para ficheros README y documentaciones varias que está bastante de moda. Shiba es un editor y previsualizador de ficheros Markdown muy potente que nos muestra las modificaciones en tiempo real.

Saludos y esperemos que os sean útiles.


## Documentación

* [Página web oficial de Electron (ENG)](https://electronjs.org/)

* [Página web oficial de Keeweb (ENG)](https://keeweb.info/)

* [Página web oficial de Chronos Timetracker (ENG)](https://chronos.web-pal.com/)

* [Página web oficial de Rambox (ENG)](https://rambox.pro/#home)

* [Página web oficial de Insomnia (ENG)](https://insomnia.rest/)

* [Página web oficial de Postman (ENG)](https://www.getpostman.com/)

* [Página web oficial de SQLelectron (ENG)](https://sqlectron.github.io/)

* [Página web oficial de DockStation (ENG)](https://dockstation.io/)

* [Página web oficial de Vagrant Manager (ENG)](https://github.com/absalomedia/vagrant-manager)

* [Página web oficial de Shiba (ENG)](https://github.com/rhysd/Shiba)


Revisado a 01/02/2020

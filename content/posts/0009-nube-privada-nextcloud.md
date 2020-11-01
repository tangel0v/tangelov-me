---
title: "Nextcloud como nube privada"
authors:
  - tangelov
date: 2018-04-24T05:00:00+02:00
tags:  ["nextcloud", "hosted"]
categories: ["cloud"]
draft: false
---

La llegada de las nubes de las grandes empresas como Amazon, Google o Microsoft y su ingente cantidad de servicios asociados (como _Office 365_ o _G Suite_) había sido precedida por una serie de sistemas de almacenamiento de datos en Internet como _Dropbox_ o _Megaupload_ y de la profileración de redes sociales como _Facebook_, _Twitter_ o _Instagram_.

A medida que estos servicios fueron generalizándose fue creciendo la preocupación acerca la integridad y la privacidad de los datos almacenados en la nube. Incluso algunos países europeos (como Dinamarca o Alemania) modificaron sus leyes nacionales para que estos datos no pudieran ser tratados fuera de las fronteras.

Para dar respuesta a estas preocupaciones, aparecieron proyectos que pretenden dar servicios similares, pero que podíamos instalar nosotros donde quisiesemos.

<!--more-->

## Owncloud y Nextcloud
En el 2010, nace de la mano del desarrollador de KDE, Frank Karlitschek un servicio de almacenamiento de ficheros, llamado _Owncloud_. Pretendía ofrecer una alternativa dentro del _Software Libre_ a los servicios de almacenamiento propietarios.

Estaba construido sobre tecnologías conocidas y comunes para facilitar su extensión. Tan sólo se necesita un servidor web, PHP y un sistema de bases de datos relacionales instalado para poder usarlo. Gracias a sus clientes para teléfonos móviles y para ordenadores, se convirtió en una alternativa a los proveedores antes citados.

Con el tiempo, fue creciendo y lo que inicialmente era un servicio de almacenamiento, fue creando un ecosistema de proveedores (que hacían sencillo su uso) y de extensiones que ampliaban la experiencia y ofrecían servicios extra como:

* Soporte de calendarios, contactos y tareas.

* Mejoras de seguridad: cifrado de servidor, punto a punto, autenticación en dos pasos.

* Capacidad de añadir otros servicios web como Webmails, etc.

Pese a su éxito, una serie de decisiones en el seno de Owncloud hicieron que en abril de 2016, Karlitschek la abandonara y creara un fork del proyecto llamado _Nextcloud_, más centrado en las necesidades de la comunidad y menos en el mercado empresarial.

## Instalación de Nextcloud
Como hemos comentado, es fácil instalar Nextcloud y tan sólo necesitamos instalar un LAMP o un LEMP stack. Es un acrónimo de _Linux_, _Apache_/_Nginx_, _MySQL_ y _PHP_.

Existen multitud de guías sobre cómo instalar Nextcloud así que simplemente voy a citar algunos ejemplos:

* [Instalación de Nextcloud en Ubuntu 18.04 sin snap](https://www.linuxbabe.com/ubuntu/install-nextcloud-ubuntu-18-04-nginx-lemp)

* [Instalación de Nextcloud en Centos 7](https://computingforgeeks.com/install-nextcloud-on-centos-with-php-apache-mariadb/)

* [Instalación de Nextcloud en Debian 10](https://chachocool.com/como-instalar-nextcloud-en-debian-10-buster/)

En general, todos ellos se basan en instalar un servidor web (Nginx o Apache), PHP (las últimas versiones aceptan PHP 7.1 o superior) y una base de datos MySQL o MariaDB. Si preferimos utilizar un método automatizado, siempre podemos instalarlo con [este playbook](https://github.com/rbicker/ansible-nextcloud)

## Usos y capacidades
La comunidad ha creado un auténtico ecosistema de extensiones y aplicaciones que hacen de Nextcloud un sistema todoterreno que podemos usar para casi todo.

Yo uso un pequeño servidor de Nextcloud instalado en una pequeña placa base (una Banana Pi, vease su [configuración](https://gitlab.com/tangelov/proyectos/blob/master/templates/apps/nextcloud-nginx-ssl)) y que utilizo para mantener un backup de determinados documentos, contactos, notas y eventos.

Tenemos aplicaciones para todo:

 [Collabora Online](https://nextcloud.com/collaboraonline/): Collabora Online es un aplicativo web que nos permite disfrutar de una suite de ofimática completa en la web. Al integrarse con Nextcloud, permite que podamos colaborar entre los distintos miembros del equipo para crear documentos o hojas de cálculo. Para entendernos, es una alternativa a Google Docs o a Office 365.

* [Mail](https://apps.nextcloud.com/apps/mail): Es una aplicación que nos permite instalar un webmail dentro de Nextcloud y que se conecta a nuestra cuenta de correo para convertir nuestra nube en un punto de entrada no sólo a nuestros ficheros sino también a nuestro correo.

* [Nextcloud Talk](https://nextcloud.com/talk/): Es una plataforma de comunicación privada, cifrada y descentralizada con aplicaciones de escritorio y móvil. Podríamos considerarlo una alternativa libre a _Google Hangouts_.

* [Passman](https://github.com/nextcloud/passman): Es un sistema de gestión de contraseñas cifradas integrado con Nextcloud. Aunque no lo uso, me parece muy potente y con muchas funcionalidades: análisis de fuerza de las contraseñas, vulnerabilidad a los diccionarios, etc.

* [News](https://apps.nextcloud.com/apps/news): Es un lector de RSS integrado directamente en Nextcloud.

* [Deck](https://apps.nextcloud.com/apps/deck): Nos brinda la posibilidad de utilizar un tablero Kanban para organizarnos dentro de nuestra nube privada.

* Todas éstas y muchas más en [su página oficial](https://apps.nextcloud.com/)

## Documentación

* [Owncloud (ENG)](https://en.wikipedia.org/wiki/Owncloud) y [Nextcloud (ENG)](https://en.wikipedia.org/wiki/Nextcloud) en la Wikipedia

* [Comparación de servicios de almacenamiento en la nube (ENG)](https://en.wikipedia.org/wiki/Comparison_of_online_backup_services)

* [Parámetros y tips en Nextcloud 17 y PHP (ENG)](https://docs.nextcloud.com/server/17/admin_manual/installation/source_installation.html#php-fpm-tips-label)

Revisado a 01/02/2020
